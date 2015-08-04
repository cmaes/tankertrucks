#!/usr/bin/python

import os
import sys
import json
import StringIO

from gurobipy import *

def mycallback(model, where):
    if where == GRB.callback.MESSAGE:
        print >>model.__output, model.cbGet(GRB.callback.MSG_STRING),

def km2mi(km):
    return 0.621371*km

def optimize(siteNames, demand, dist, capacity, output=False):

    sites = range(len(siteNames))
    clients = sites[1:]

    model = Model('Diesel Fuel Delivery')

    if not output:
        model.params.OutputFlag = 0

    prec = {}
    for i in sites:
        for j in sites:
            prec[i,j] = model.addVar(vtype=GRB.BINARY)

    quant = {}
    for i in clients:
        quant[i] = model.addVar(lb=demand[i],ub=capacity)

    model.update()

    obj = quicksum( dist[i][j]*prec[i,j] for i in sites for j in sites if i != j )

    model.setObjective(obj)

    for j in clients:
        model.addConstr(quicksum( prec[i,j] for i in sites if i != j ) == 1)
    for i in clients:
        model.addConstr(quicksum( prec[i,j] for j in sites if i != j ) == 1)

    for i in clients:
        model.addConstr(quant[i] <= capacity + (demand[i] - capacity)*prec[0,i])

    # for i in clients:
    #     for j in clients:
    #         if i != j:
    #             model.addConstr(quant[j] >= quant[i] + demand[j] - capacity + \
    #                                 capacity*prec[i,j] + (capacity - demand[j] - demand[i])*prec[j,i])

    for i in clients:
        for j in clients:
            if i != j:
                model.addConstr(quant[i] - quant[j] + capacity*prec[i,j] <= capacity - demand[j])


    model.update()

    output = StringIO.StringIO()
    model.__output = output

    model.optimize(mycallback)

    quant = model.getAttr("X", quant)
    quant[0] = 0

    prec = model.getAttr("X", prec)

    def printTour(i, distance, count, output):
        if prec[i, 0] > 0.5:
            print >>output, "Tanker %d drives %g mi from %s to %s." \
                % (count, km2mi(dist[i][0]), siteNames[i], siteNames[0])
            distance = distance + dist[i][0]
            print >>output, "Distance driven by Tanker %d: %g mi" % (count, km2mi(distance))
            print >>output, "Volume in Tanker %d: %g liters\n\n" % (count, quant[i])
            return
        for j in clients:
            if prec[i,j] > 0.5:
                print >>output, "Tanker %d drives %g mi from %s to %s." % \
                    (count, km2mi(dist[i][j]), siteNames[i],siteNames[j])
                print >>output, "\tDelivers %g liters of oil to %s." % \
                    (quant[j] - quant[i], siteNames[j])
                print >>output, "\tDemand at %s was %g liters.\n" % (siteNames[j], demand[j])
                printTour(j, distance + dist[i][j], count, output)
                count = count + 1
        return count-1


    def calcTour(i, tour):
        tours = []
        if prec[i, 0] > 0.5:
            tour.append(siteNames[0])
            return tour
        for j in clients:
            if prec[i,j] > 0.5:
                tour.append(siteNames[j])
                calcTour(j, tour)
                tours.append(tour)
                tour = [siteNames[0]]
        return tours

    def tankvolume(volume):
        tankvol = []
        total = volume[-1]
        for i in range(len(volume)-1):
            tankvol.append(total - volume[i])
        tankvol.append(0)
        return tankvol

    def calcVolumes(i, volume):
        volumes = []
        if prec[i,0] > 0.5:
            return volume
        for j in clients:
            if prec[i,j] > 0.5:
                volume.append(quant[j])
                calcVolumes(j, volume)
                volumes.append(tankvolume(volume))
                volume = [0]
        return volumes

    print >>output, "\n"
    print >>output, '-'*80
    print >>output, "\n"
    count = printTour(0, 0, 1, output)
    print >>output, "Total distance driven: %g mi" % km2mi(model.ObjVal)
    print >>output,  "Total tankers needed: %d" % count
    contents = output.getvalue()
    output.close()
    retdict = { 'tours' : calcTour(0, [siteNames[0]]),
                'directions' : contents,
                'volumes' : calcVolumes(0, [0])
                }

    return retdict

def handleoptimize(jsdict):
    if 'siteNames' and 'demand' and 'dist' and 'capacity' in jsdict:
        jsout = optimize(jsdict['siteNames'], jsdict['demand'], jsdict['dist'], jsdict['capacity'])
        return jsout

if __name__ == '__main__':
    jsdict = json.load(sys.stdin)
    jsdict = handleoptimize(jsdict)
    print 'Content-Type: application/json\n\n'
    print json.dumps(jsdict)
