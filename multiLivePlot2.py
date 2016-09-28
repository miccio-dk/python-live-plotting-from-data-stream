""" Live plotting of data recieved using through socket/serial connection. This version is slower that the one using 
    animation, but in this version the axes-ticks are correct. """

import sys
import time
import numpy as np
from matplotlib import pyplot as plt

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

n = 1000


def getLinesPerType(label, reader):
    s, data = reader(dtype=float)
    if s == label:
        if 1 < len(data) <= 15:
            return len(data)
    return getLinesPerType(label, reader)

def press(event):
    if event.key == 'x':
        for s in min_:
            min_[s] = float('inf')
        for s in max_:
            max_[s] = -float('inf')

    elif event.key == 'q':
        plt.close(event.canvas.figure)
        reader.closeConnection()
        sys.exit()

reader = Reader()

axs = {}
lineSets = {}
rings = {}
xs = {}
indexes = {}
min_ = {}
max_ = {}
ls = {}

fig = plt.figure()
fig.canvas.mpl_connect('key_press_event', press)
for i, s in enumerate(labels):
    ax = fig.add_subplot(len(labels), 1, i + 1)
    axs[s] = ax
    ax.set_xlim(0, n)
    ax.set_ylim(-2, 2)
    lineSets[s] = []
    ls[s] = getLinesPerType(s, reader)
    for j in range(ls[s]):
        lineSets[s].append(ax.plot([], [], '.', label=chr(ord('a')+j))[0])
    ax.set_title(s)
    ax.legend(loc=2)
    rings[s] = np.zeros((n, ls[s]))
    xs[s] = np.zeros(n)
    indexes[s] = 0
    min_[s] = float('inf')
    max_[s] = -float('inf')

print("\nNumber of data points in each label:")
print(ls)

print("\nPress x to resize y axes. Press q to quit.")

timeNow = time.time()
c = 0
while True:
    s, data = reader(dtype=float)
    c += 1
    if s in labels and len(data) == ls[s]:
        N = indexes[s] % n
        rings[s][N, :] = data
        xs[s][N] = indexes[s]
        indexes[s] += 1
        if time.time() - timeNow > 0.3:
            for s in labels:
                for j in range(ls[s]):
                    lineSets[s][j].set_data(xs[s], rings[s][:, j])
                if rings[s].min() < min_[s]:
                    if rings[s].min() == 0 and c < n:
                        rings[s][N:, :] = data.min()

                    min_[s] = rings[s].min()
                    axs[s].set_ylim(min_[s], max_[s])
                if rings[s].max() > max_[s]:
                    if rings[s].max() == 0 and c < n:
                        rings[s][N:, :] = data.max()

                    max_[s] = rings[s].max()
                    axs[s].set_ylim(min_[s], max_[s])
                axs[s].set_xlim(indexes[s] - n, indexes[s])
            plt.pause(0.001)
            timeNow = time.time()
    else:
        print(s)
