""" Live plotting using animation of data recieved using through socket/serial connection. Only reason to not use this
    version is that the axes-ticks are not updated as data is received. """

import sys
import time
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation


class MultiLivePlotAni(object):
    def __init__(self, labels, reader, n):
        self.labels = labels
        self.reader = reader
        # Mostly plotting related stuff from here on
        self.n = n
        self.axs = {}
        self.lineSets = {}
        self.rings = {}
        self.xs = {}
        self.indexes = {}
        self.min_ = {}
        self.max_ = {}
        self.ls = {}

        self.fig = plt.figure()
        self.fig.canvas.mpl_connect('key_press_event', self.press)
        # ax = self.fig.add_subplot(1, 1, 1)
        for i, s in enumerate(labels):
            ax = self.fig.add_subplot(len(labels), 1, i + 1)
            self.axs[s] = ax
            ax.set_xlim(0, n)
            ax.set_ylim(-2, 2)
            self.lineSets[s] = []
            self.ls[s] = self.getLinesPerType(s, reader)
            for j in range(self.ls[s]):
                self.lineSets[s].append(ax.plot([], [], '.', label=chr(ord('a') + j))[0])
            ax.set_title(s)
            ax.legend(loc=2)
            self.rings[s] = np.zeros((n, self.ls[s]))
            self.xs[s] = np.zeros(n)
            self.indexes[s] = 0
            self.min_[s] = float('inf')
            self.max_[s] = -float('inf')

        print("\nNumber of data points in each label:")
        print(self.ls)

        print("\nPress x to resize y axes. Press q to quit.")

    def run(self):
        anim = FuncAnimation(self.fig, self.update_lines, interval=10, blit=True)
        plt.show()

    def getData(self):
        s, data = self.reader(dtype=float)
        if s in self.labels and len(data) == self.ls[s]:
            N = self.indexes[s] % self.n
            self.rings[s][N, :] = data
            self.xs[s][N] = self.indexes[s]
            self.indexes[s] += 1
        else:
            print(s)

    def press(self, event):
        if event.key == 'x':
            for s in self.min_:
                self.min_[s] = float('inf')
            for s in self.max_:
                self.max_[s] = -float('inf')

        elif event.key == 'q':
            plt.close(event.canvas.figure)
            self.reader.closeConnection()
            sys.exit()

    def update_lines(self, frame):
        timeAtStart = time.time()
        while time.time() - timeAtStart < 0.1:
            self.getData()

        for s in self.labels:
            for j in range(self.ls[s]):
                self.lineSets[s][j].set_data(self.xs[s], self.rings[s][:, j])
            if self.rings[s].min() < self.min_[s]:
                self.min_[s] = self.rings[s].min()
                self.axs[s].set_ylim(self.min_[s], self.max_[s])
            if self.rings[s].max() > self.max_[s]:
                self.max_[s] = self.rings[s].max()
                self.axs[s].set_ylim(self.min_[s], self.max_[s])
            self.axs[s].set_xlim(self.indexes[s] - self.n, self.indexes[s])
        return sum([self.lineSets[s] for s in self.labels], [])

    def getLinesPerType(self, label, reader):
        s, data = self.reader(dtype=float)
        if s == label:
            if 1 < len(data) <= 15:
                return len(data)
        return self.getLinesPerType(label, reader)
