""" Live plotting of data recieved using through socket/serial connection. This version is slower that the one using
    animation, but in this version the axes-ticks are correct. """

import sys
import time
import numpy as np
from matplotlib import pyplot as plt


class MultiLivePlot(object):
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
        maxTries = 10
        for i, s in enumerate(labels):
            ax = self.fig.add_subplot(len(labels), 1, i + 1)
            self.axs[s] = ax
            ax.set_xlim(0, n)
            ax.set_ylim(-2, 2)
            self.lineSets[s] = []
            for i in range(maxTries):
                length = self.getLinesPerType(s, reader)
                if length is not None:
                    print(length)
                    self.ls[s] = length
                    break
            for j in range(self.ls[s]):
                self.lineSets[s].append(ax.plot([], [], '.', label=chr(ord('a')+j))[0])
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

        self.timeNow = time.time()
        self.c = 0

    def update(self):
        self.c += 1
        s, data = self.getData()
        if s in self.labels and len(data) == self.ls[s]:

            if time.time() - self.timeNow > 0.03:
                self.updatePlot(data)
                self.timeNow = time.time()
        else:
            print(s)

    def updatePlot(self, data):
        for s in self.labels:
            for j in range(self.ls[s]):
                self.lineSets[s][j].set_data(self.xs[s], self.rings[s][:, j])
            if self.rings[s].min() < self.min_[s]:
                if self.rings[s].min() == 0 and self.c < self.n:
                    self.rings[s][self.N:, :] = data.min()

                self.min_[s] = self.rings[s].min()
                self.axs[s].set_ylim(self.min_[s], self.max_[s])
            if self.rings[s].max() > self.max_[s]:
                if self.rings[s].max() == 0 and self.c < self.n:
                    self.rings[s][self.N:, :] = data.max()

                self.max_[s] = self.rings[s].max()
                self.axs[s].set_ylim(self.min_[s], self.max_[s])
            self.axs[s].set_xlim(self.indexes[s] - self.n, self.indexes[s])
        plt.pause(0.001)

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

    def getData(self):
        s, data = self.reader(dtype=float)
        if s in self.labels and len(data) == self.ls[s]:
            self.N = self.indexes[s] % self.n
            self.rings[s][self.N, :] = data
            self.xs[s][self.N] = self.indexes[s]
            self.indexes[s] += 1
        else:
            print(s)
        return s, data

    def getLinesPerType(self, label, reader):
        s, data = self.reader(dtype=float)
        if s == label:
            if 0 < len(data) <= 15:
                return len(data)
        return None
