export GUROBI_HOME      := /tmp/gurobi604/linux64
export LD_LIBRARY_PATH  := $(GUROBI_HOME)/lib
export PYTHONPATH       := $(LD_LIBRARY_PATH)/python2.7/

all:
	python SimpleServer.py


test:
	echo '{"capacity": 3900, "siteNames": ["Reno", "South Lake Tahoe", "Carson City", "Garnerville, NV", "Fernely, NV"], "dist": [[0, 98, 50, 80, 55], [100, 0, 44, 33, 124], [51, 44, 0, 26, 80], [81, 33, 26, 0, 106], [55, 124, 79, 106, 0]], "demand": [0, 1000, 1200, 1600, 1400]}' | python tankertrucks.py
