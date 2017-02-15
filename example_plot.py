#!/usr/bin/env python3
import sys
from plotter import Plotter

allGood = True
if len(sys.argv) > 1:
    if sys.argv[1] == 'serial':
        from serial_reader import Reader
        reader = Reader(port='/dev/ttyUSB0', baudrate=115200)

    elif sys.argv[1] == 'socket':
        from socket_reader import Reader
        reader = Reader('10.0.102.2', port=50007)

    elif sys.argv[1] == 'pipe':
        from pipe_reader import Reader
        reader = Reader()

    else:
        allGood = False
    if len(sys.argv) > 2:
        labels = sys.argv[2:]
    else:
        labels = []
else:
    allGood = False

if not allGood:
    print("Usage: <reader (serial/socket)> <labels (optional)>")
    sys.exit()

# Number of data "packages" to plot at the same time
n = 1000

plotParams = {}
plotHandler = Plotter(labels, reader, n, plotParams)
while True:
    plotHandler.update()
