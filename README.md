# Tanker Trucks
An example of using Gurobi to route vehicles

![](sample2.png?raw=true)

# Running the example

1. Start Python's webserver from the command line
    ```
    make
    ```

2. Point your browser at http://localhost:8000

3. Add some orders in the demo area.

4. Click "Compute Optimal Delivery Route" to find the optimal routes.

# Performing an optimization

To just solve the model (without running a web server) do:

```
make test
```
