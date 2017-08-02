import sys
import time
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

matplotlib.rcParams['toolbar'] = 'None'


def load_src(name, fpath):
  import os
  import imp
  return imp.load_source(name, os.path.join(os.path.dirname(__file__), fpath))


mt = load_src('mathTools', 'quaternion/quaternion.py')


class QuadPlotter(object):
  def __init__(self, reader, quaLabel, posLabel=None, axis=False):
    self.reader = reader
    self.quaLabel = quaLabel
    self.posLabel = posLabel
    self.reader = reader
    self.fig = plt.figure()
    self.fig.canvas.mpl_connect('key_press_event', self.press)
    self.ax = self.fig.add_subplot(1, 1, 1, aspect='equal', projection='3d')
    self.lines = [self.ax.plot([], [], [], 'r', linewidth=3)[0],
                  self.ax.plot([], [], [], 'g', linewidth=3)[0],
                  self.ax.plot([], [], [], 'b', linewidth=3)[0]]
    self.ax.set_xlabel("x")
    self.ax.set_ylabel("y")
    self.ax.set_zlabel("z")


    if not axis:
      self.ax.set_xlim3d(-0.2, 0.2)
      self.ax.set_ylim3d(-0.2, 0.2)
      self.ax.set_zlim3d(-0.2, 0.2)
      self.ax.set_axis_off()
    else:
      self.ax.set_xlim3d(-1.0, 1.0)
      self.ax.set_ylim3d(-1.0, 1.0)
      self.ax.set_zlim3d(-1.0, 1.0)


    self.latestPos = np.zeros(3)
    self.latestQua = None

    self.timeBetweenPlotUpdates = 0.03
    self.timeAtLastPlotUpdate = 0

  def press(self, event):
    if event.key == 'q':
      plt.close(event.canvas.figure)
      sys.exit()

  def drawQuad(self, q, pos):
    lineX = q.rotateVectors(np.array([[-0.3,    0, 0], [0.3,   0,   0]]).T)
    lineY = q.rotateVectors(np.array([[   0, -0.3, 0], [  0, 0.3,   0]]).T)
    lineZ = q.rotateVectors(np.array([[   0,    0, 0], [  0,   0, 0.15]]).T)

    self.lines[0].set_xdata(lineX[0, :] + pos[0])
    self.lines[0].set_ydata(lineX[1, :] + pos[1])
    self.lines[0].set_3d_properties(lineX[2, :] + pos[2])
    self.lines[1].set_xdata(lineY[0, :] + pos[0])
    self.lines[1].set_ydata(lineY[1, :] + pos[1])
    self.lines[1].set_3d_properties(lineY[2, :] + pos[2])
    self.lines[2].set_xdata(lineZ[0, :] + pos[0])
    self.lines[2].set_ydata(lineZ[1, :] + pos[1])
    self.lines[2].set_3d_properties(lineZ[2, :] + pos[2])
    plt.pause(0.001)

  def update(self):
    label, data, isNumerical = self.reader()
    if isNumerical and label == self.quaLabel:
      self.latestQua = mt.Quaternion(*data)
      if time.time() - self.timeAtLastPlotUpdate > self.timeBetweenPlotUpdates:
        self.drawQuad(self.latestQua, self.latestPos)
        self.timeAtLastPlotUpdate = time.time()
    elif isNumerical and self.posLabel is not None and label == self.posLabel:
      self.latestPos = data
