import sys
import numpy as np
import time

allGood = 0
if len(sys.argv) > 2:
    allGood = 1
    if sys.argv[1] == 'serial':
        from serial_reader import Reader
    elif sys.argv[1] == 'socket':
        from socket_reader import Reader
    else:
        allGood = 0
    labels = sys.argv[2:]
    nLabels = len(labels)

if not allGood:
    print("Usage: <reader (serial/socket)> <label(s)>")
    sys.exit()

# Socket:
if sys.argv[1] == 'socket':
    reader = Reader(port=50007)

# Serial:
if sys.argv[1] == 'serial':
    reader = Reader(port='/dev/ttyUSB0', baudrate=115200)


data = {}
indeces = {}
for label in labels:
    # Empty files
    f = open(label, 'w')
    f.close()

    data[label] = np.zeros((100, 3))
    indeces[label] = 0


lastTime = time.time()
while True:
    label, dataPoint = reader(dtype=float)
    if label in labels:
        data[label][indeces[label], :] = dataPoint
        indeces[label] += 1

        if indeces[label] == data[label].shape[0] - 1:
            data[label] = np.vstack((data[label], np.zeros(data[label].shape)))
        if time.time() - lastTime > 1:
            for label in labels:
                print("Recieved {:} data points with label {:}".format(indeces[label], label))
                np.savetxt(label, data[label][:indeces[label], :])
            lastTime = time.time()