""" Live plotting of data received by one of the readers """

import sys
import time
import collections
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from ring import Ring

# Set line colors to match those of matplotlib 2.0
if int(matplotlib.__version__.split('.')[0]) < 2:
    matplotlib.rcParams["axes.color_cycle"] = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]

# Remove matplotlibs default keybindings
for k, v in sorted(plt.rcParams.items()):
    if k.startswith('keymap'):
        plt.rcParams[k] = []


class MissingLabelError(Exception):
    pass


class Plotter(object):
    def __init__(self, labels, reader, ringLength, plotParams={}):
        self.reader = reader
        self.ringLength = ringLength
        self.plotParams = plotParams
        self.fig = plt.figure()
        self.fig.canvas.mpl_connect('key_press_event', self.press)
        if labels:
            self.setUp(labels)
        else:
            self.labels = labels

        self.lastPlotUpdate = time.time()
        self.freezePlot = False
        self.receivingCommand = False
        self.command = ''
        self.rings = {}

    def setUp(self, labels):
        if not labels:
            print("No labels specified - Trying to find them automatically..")
            self.labels = discoverLabels(self.reader)
            print("Found labels: {:}".format(', '.join(self.labels)))
        else:
            self.labels = labels

        self.freezePlot = False
        self.rings = {}

        textColor = 230/255
        windowColor = 11/255
        plotBackgroundColor = 22/255

        self.fig.canvas.mpl_connect('key_press_event', self.press)
        self.fig.patch.set_facecolor((windowColor,)*3)
        for i, s in enumerate(self.labels):
            ax = self.fig.add_subplot(len(self.labels), 1, i + 1, axisbg=(plotBackgroundColor,)*3)
            packageLength = getLinesPerType(s, self.reader)
            self.rings[s] = Ring(packageLength, self.ringLength)
            self.rings[s].lineSets = []
            for j in range(packageLength):
                self.rings[s].lineSets.append(ax.plot([], [], '.', label=chr(ord('a')+j), **self.plotParams)[0])
            ax.set_title(s, color=(textColor,)*3)
            ax.legend(loc=2)
            ax.xaxis.label.set_color((textColor,)*3)
            # ax.yaxis.label.set_color((textColor,)*3)
            ax.tick_params(axis='x', colors=(textColor,)*3)
            ax.tick_params(axis='y', colors=(textColor,)*3)
            self.rings[s].ax = ax

        print("\nNumber of data points for each label:")
        for s in self.labels:
            print("{:}: {:} ".format(s, self.rings[s].nY))

    def update(self):
        self.getData()
        if time.time() - self.lastPlotUpdate > 0.03:
            self.updatePlotData()
            self.lastPlotUpdate = time.time()

    def updatePlotData(self):
        if not self.freezePlot:
            for ring in self.rings.values():
                for j in range(ring.nY):
                    ring.lineSets[j].set_data(ring.xs, ring.yData[j, :])

                delta = (ring.maxY - ring.minY) * 0.1
                ring.ax.set_ylim(ring.minY - delta, ring.maxY + delta)
                ring.ax.set_xlim(ring.xs[ring.head] - ring.length, ring.xs[ring.head])
                ring.looseTail()

            plt.pause(0.001)

            for ring in self.rings.values():
                ring.fixTail()

    def press(self, event):
        if self.receivingCommand:
            if event.key == 'enter':
                self.receivingCommand = False
                print("Sending '{:}'".format(self.command))
                self.reader.write(self.command + "\r\n")
                self.command = ''
            else:
                self.command += event.key
            return

        if event.key == 'x':
            for ring in self.rings.values():
                ring.reset()

        elif event.key == 'p':
            self.freezePlot = not self.freezePlot

        elif event.key == 'r':
            self.fig.clear()
            self.setUp([])

        elif event.key == 'g':
            self.fig.savefig('{:.0f}.png'.format(time.time()), bbox_inches='tight')

        elif event.key == 'enter':
            print("listening for message until next enter key press:")
            self.receivingCommand = True

        elif event.key == 'q':
            plt.close(event.canvas.figure)
            self.reader.closeConnection()
            sys.exit()

    def getData(self):
        s, data, isNumerical = self.reader()
        if isNumerical and s in self.labels and len(data) == self.rings[s].nY:
            self.rings[s].update(data)
        elif isCommand(s):
            event = FakeKeyEvent(data[0].strip())
            print("Received command in data stream: {}".format(event.key))
            self.press(event)
        else:
            if s:
                if len(data) == 0:
                    print(s)
                else:
                    print(s, *data)


class FakeKeyEvent(object):
    def __init__(self, key):
        self.key = key


def isCommand(s):
    if s == 'COMMAND':
        return True


def discoverLabels(reader):
    # There must be a smarter/prettier way - but it does seem to be pretty robust
    maxTries = 100
    print("Discovering labels by looking at the first {} packages...".format(maxTries))
    seenLabels = collections.defaultdict(int)
    for _ in range(maxTries):
        s, data, isNumerical = reader()
        if s:
          if isNumerical:
            seenLabels[s] += 1
        else:
            # time.sleep(0.05)
            pass

    # Good for noisy data for equal data rates:
    # possibleLabels = [('dummy', 1)] + sorted(seenLabels.items(), key=lambda x: x[1])
    # diffs = []
    # for i in range(len(possibleLabels)-1):
    #     diffs.append(possibleLabels[i+1][1] - possibleLabels[i][1])
    # threshold = np.argmax(diffs) + 1
    # return sorted(list(zip(*possibleLabels))[0][threshold:])

    # Good for not too noisy data for different data rates
    maxExpectedLabels = 10
    threshold = maxTries / maxExpectedLabels
    possibleLabels = [l for l, s in seenLabels.items() if s >= threshold]
    return sorted(possibleLabels)


def getLinesPerType(label, reader):
    maxTries = 100
    seenLabels = collections.defaultdict(int)
    for _ in range(maxTries):
        s, data, isNumerical = reader()
        if isNumerical:
            seenLabels[s] += 1
            if s == label and 0 < len(data) <= 15:
                return len(data)
    pretty = '\n'.join([k + ': ' + str(v) for k, v in seenLabels.items()])
    raise MissingLabelError("Label: '{:}' not found after receiving {:} data packages\nReceived labels:\n{:}".format(label, maxTries, pretty))
