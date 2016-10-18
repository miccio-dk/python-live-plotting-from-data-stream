""" Live plotting of data received one of the readers """

import sys
import time
import collections
import numpy as np
from matplotlib import pyplot as plt


class MissingLabelError(Exception):
    pass


class MultiLivePlot(object):
    def __init__(self, labels, reader, n):
        self.reader = reader
        if not labels:   # PEP 8 style guide
            print("No labels specified - Trying to find them automatically..")
            self.labels = self.discoverLabels()
            print("Found labels: {:}".format(', '.join(self.labels)))
        else:
            self.labels = labels
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
        for i, s in enumerate(self.labels):
            ax = self.fig.add_subplot(len(self.labels), 1, i + 1)
            self.axs[s] = ax
            ax.set_xlim(0, n)
            ax.set_ylim(-2, 2)
            self.lineSets[s] = []
            for i in range(maxTries):
                length = self.getLinesPerType(s, reader)
                if length is not None:
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
        self.running = True

    def update(self):
        if self.running:
            s, data = self.getData()
            if s in self.labels and len(data) == self.ls[s]:
                if time.time() - self.timeNow > 0.03:
                    self.updatePlot(data)
                    self.timeNow = time.time()
            if self.c == 100:
                print('resetting')
                self.reset()
            self.c += 1
        else:
            plt.pause(0.001)

    def updatePlot(self, data):
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
        plt.pause(0.001)

    def reset(self):
        for label in self.labels:
            self.rings[label] = np.zeros((self.n, self.ls[label])) + self.rings[label][self.N, :]
            self.xs[label] = np.zeros(self.n)
            self.indexes[label] = 0
            self.min_[label] = float('inf')
            self.max_[label] = -float('inf')


    def press(self, event):
        if event.key == 'x':
            self.reset()

        elif event.key == 'p':
            self.running = not self.running

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
        maxTries = 100
        seenLabels = collections.defaultdict(int)
        for _ in range(maxTries):
            s, data = self.reader(dtype=float)
            seenLabels[s] += 1
            if s == label and 0 < len(data) <= 15:
                return len(data)
        pretty = '\n'.join([k + ': ' + str(v) for k, v in seenLabels.items()])
        raise MissingLabelError("Label: '{:}' not found after receiving {:} data packages\nReceived labels:\n{:}".format(label, maxTries, pretty))

    def discoverLabels(self):
        # There must be a smarter/prettier way - but it does seem to be pretty robust
        maxTries = 100
        seenLabels = collections.defaultdict(int)
        for _ in range(maxTries):
            s, data = self.reader(dtype=float)
            seenLabels[s] += 1
        possibleLabels = [('dummy', 1)] + sorted(seenLabels.items(), key=lambda x: x[1])
        diffs = []
        for i in range(len(possibleLabels)-1):
            diffs.append(possibleLabels[i+1][1] - possibleLabels[i][1])
        threshold = np.argmax(diffs) + 1
        return list(zip(*possibleLabels))[0][threshold:]
