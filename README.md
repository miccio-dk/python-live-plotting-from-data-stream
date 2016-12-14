# Live Plotting Using Python

Continuously reads and plots data following the format:
"labelA,val0,val1,...,valN"

The following is an example of a correctly formatted package "acc,0.123,0.234,0.135"

The plotter creates a subplot for each type of package. Packages are distinguished by their label only and can have any (constant) number of values.
The readers (socket, serial or pipe) reads a string of data following the above format and tries to convert it into a list of floats/int

To see a working example or to test functionality use writer.py and example_plot.py:

python writer.py pipe | python example_plot.py pipe

![Example of using three different packages](https://github.com/erikbrntsn/python-live-plotting-from-data-stream/blob/master/documentation/example_plot.png)
