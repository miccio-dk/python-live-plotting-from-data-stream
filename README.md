# Live Plotting Using Python

Continuously reads and plots data following the format:
"labelA,val0,val1,...,valN"

The following is an example of a correctly formatted package "acc,0.123,0.234,0.135"

The plotter creates a subplot for each type of package. Packages are distinguished by their label only and can have any (constant) number of values.
The readers (socket, serial or pipe) reads a string of data following the above format and tries to convert it into a list of floats/int
