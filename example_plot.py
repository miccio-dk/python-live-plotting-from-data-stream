import sys
from multiLivePlot import MultiLivePlot as plotter

if len(sys.argv) > 1:
    if sys.argv[1] == 'serial':
        from serial_reader import Reader
        reader = Reader(port='/dev/ttyUSB0', baudrate=115200)

    elif sys.argv[1] == 'socket':
        from socket_reader import Reader
        reader = Reader(port=50007)

    elif sys.argv[1] == 'pipe':
        from pipe_reader import Reader
        reader = Reader()

    else:
        print("Usage: <reader (serial/socket)> <labels (optional)>")
        sys.exit()
    if len(sys.argv) > 2:
        labels = sys.argv[2:]
    else:
        labels = []

# Number data "packages" to plot at the same time
n = 1000

plotHandler = plotter(labels, reader, n)
while True:
    plotHandler.update()
