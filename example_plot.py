import sys
from plotter import Plotter

allGood = True
if len(sys.argv) > 1:
    if sys.argv[1] == 'serial':
        from serial_reader import Reader
        reader = Reader(port='/dev/ttyUSB0', baudrate=115200)

    elif sys.argv[1] == 'socket':
        from socket_reader_client import Reader
        reader = Reader('10.0.2.50', port=50007)
        # from socket_reader import Reader
        # reader = Reader(port=50007)

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

plotHandler = Plotter(labels, reader, n)
while True:
    plotHandler.update()
