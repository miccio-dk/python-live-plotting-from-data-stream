import sys
from multiLivePlot import MultiLivePlotAni as plotter
# from multiLivePlot2 import MultiLivePlot as plotter

allGood = 0
if len(sys.argv) > 2:
    allGood = 1
    if sys.argv[1] == 'serial':
        from serial_reader import Reader
    elif sys.argv[1] == 'socket':
        from socket_reader import Reader
    elif sys.argv[1] == 'pipe':
        from pipe_reader import Reader
    else:
        allGood = 0
    labels = sys.argv[2:]
    nLabels = len(labels)

if not allGood:
    print("Usage: <reader (serial/socket)> <label(s)>")
    sys.exit()


# Number data "packages" to plot at the same time
n = 1000

# Socket:
# reader = Reader(port=50007)

# Serial:
# reader = Reader(port='/dev/ttyUSB0', baudrate=115200)

# Pipe
reader = Reader()

plotHandler = plotter(labels, reader, n)

# MultiLivePlot:
# while True:
#     plotHandler.update()

# MultiLivePlotAni
plotHandler.run()
