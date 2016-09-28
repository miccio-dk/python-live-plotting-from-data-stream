""" Live plotting using animation of data recieved using through socket/serial connection. Only reason to not use this
    version is that the axes-ticks are not updated as data is received. """

import sys
import time
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

if len(sys.argv) > 1:
    nSensors = len(sys.argv) - 1
    labels = [sys.argv[s + 1] for s in range(nSensors)]
    if len(sys.argv) > 2 and sys.argv[2] == 'serial':
        from serial_reader import Reader
    else:
        from socket_reader import Reader
else:
    print("Specify label(s)")
    sys.exit()

n = 1000


def getData():
    s, data = reader(dtype=float)
    if s in labels and len(data) == ls[s]:
        N = indexes[s] % n
        rings[s][N, :] = data
        xs[s][N] = indexes[s]
        indexes[s] += 1
    else:
        print(s)


def press(event):
    if event.key == 'x':
        for s in min_:
            min_[s] = float('inf')
        for s in max_:
            max_[s] = -float('inf')

    elif event.key == 'q':
        plt.close(event.canvas.figure)


def update_lines(frame):
    timeAtStart = time.time()
    while time.time() - timeAtStart < 0.1:
        getData()

    for s in labels:
        for j in range(ls[s]):
            lineSets[s][j].set_data(xs[s], rings[s][:, j])
        if rings[s].min() < min_[s]:
            min_[s] = rings[s].min()
            axs[s].set_ylim(min_[s], max_[s])
        if rings[s].max() > max_[s]:
            max_[s] = rings[s].max()
            axs[s].set_ylim(min_[s], max_[s])
        axs[s].set_xlim(indexes[s] - n, indexes[s])
    return sum([lineSets[s] for s in labels], [])


def getLinesPerType(label, reader):
    s, data = reader(dtype=float)
    if s == label:
        if 1 < len(data) <= 15:
            return len(data)
    return getLinesPerType(label, reader)

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
ax = fig.add_subplot(1, 1, 1)
for i, s in enumerate(labels):
    ax = fig.add_subplot(len(labels), 1, i + 1)
    axs[s] = ax
    ax.set_xlim(0, n)
    ax.set_ylim(-2, 2)
    lineSets[s] = []
    ls[s] = getLinesPerType(s, reader)
    for j in range(ls[s]):
        lineSets[s].append(ax.plot([], [], '.', label=chr(ord('a') + j))[0])
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
anim = FuncAnimation(fig, update_lines, interval=10, blit=True)
plt.show()
