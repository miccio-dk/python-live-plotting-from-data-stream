#!/usr/bin/env python3

import time
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from ring import Ring


def load_src(name, fpath):
  import os
  import imp
  return imp.load_source(name, os.path.join(os.path.dirname(__file__), fpath))


mt = load_src('mathTools', 'quaternion/quaternion.py')


def drawQuad(q, lines, pos):
  lineX = q.rotateVectors(np.array([[0.3,   0,   0], [-0.3,    0, 0]]).T)
  lineY = q.rotateVectors(np.array([[  0, 0.3,   0], [   0, -0.3, 0]]).T)
  lineZ = q.rotateVectors(np.array([[  0,   0, 0.3], [   0,    0, 0]]).T)

  lines[0].set_xdata(lineX[0, :] + pos[0])
  lines[0].set_ydata(lineX[1, :] + pos[1])
  lines[0].set_3d_properties(lineX[2, :] + pos[2])
  lines[1].set_xdata(lineY[0, :] + pos[0])
  lines[1].set_ydata(lineY[1, :] + pos[1])
  lines[1].set_3d_properties(lineY[2, :] + pos[2])
  lines[2].set_xdata(lineZ[0, :] + pos[0])
  lines[2].set_ydata(lineZ[1, :] + pos[1])
  lines[2].set_3d_properties(lineZ[2, :] + pos[2])


class PathPlot(object):
  def __init__(self, reader, qLabel="q", pCLabel="pC", pDLabel="pD"):
    # Quaternion, pathCurrent, pathDesired
    self.qLabel = qLabel
    self.pCLabel = pCLabel
    self.pDLabel = pDLabel
    self.reader = reader
    self.fig = plt.figure()
    self.fig.canvas.mpl_connect('key_press_event', self.press)
    self.ax = self.fig.add_subplot(1, 1, 1, projection='3d', aspect='equal')
    self.ax.set_xlim3d(-2, 2)
    self.ax.set_ylim3d(-2, 2)
    self.ax.set_zlim3d(-2, 2)
    self.ax.set_xlabel('x')
    self.ax.set_ylabel('y')
    self.ax.set_zlabel('z')

    self.pathLines = {}
    # Actual position
    self.pathLines[self.pCLabel] = (self.ax.plot([], [], [], 'b.')[0])
    # Desired position
    self.pathLines[self.pDLabel] = (self.ax.plot([], [], [], 'r.')[0])

    # Quad
    self.quadLines = []
    self.quadLines.append(self.ax.plot([], [], [], 'r', linewidth=2)[0])
    self.quadLines.append(self.ax.plot([], [], [], 'g', linewidth=2)[0])
    self.quadLines.append(self.ax.plot([], [], [], 'b', linewidth=2)[0])

    self.lastPlotUpdate = time.time()
    self.rings = {}
    self.rings[self.pCLabel] = Ring(3, 1000)
    self.rings[self.pDLabel] = Ring(3, 1000)
    self.rings[self.qLabel] = Ring(4, 1000)


  def update(self):
    self.getData()
    if time.time() - self.lastPlotUpdate > 0.03:
      self.updatePlotData()
      self.lastPlotUpdate = time.time()


  def updatePlotData(self):
    # Set data for each line
    self.pathLines[self.pCLabel].set_data(self.rings[self.pCLabel].yData[0, :], self.rings[self.pCLabel].yData[1, :])
    self.pathLines[self.pCLabel].set_3d_properties(self.rings[self.pCLabel].yData[2, :])

    self.pathLines[self.pDLabel].set_data(self.rings[self.pDLabel].yData[0, :], self.rings[self.pDLabel].yData[1, :])
    self.pathLines[self.pDLabel].set_3d_properties(self.rings[self.pDLabel].yData[2, :])

    newestQua = mt.Quaternion(*self.rings[self.qLabel].newest())
    newestPos = self.rings[self.pCLabel].newest()
    drawQuad(newestQua, self.quadLines, newestPos)

    plt.pause(0.001)


  def getData(self):
    s, data, isNumerical = self.reader()
    if isNumerical and s in self.rings and len(data) == self.rings[s].nY:
      self.rings[s].update(data)
    else:
      if s:
        if len(data) == 0:
          print(s)
        else:
          print(s, *data)


  def press(self, event):
    # Close and quit
    if event.key == 'q':
      plt.close(event.canvas.figure)
      self.reader.closeConnection()
      exit()



if __name__ == "__main__":
  import sys
  from pipe_reader import Reader

  print(sys.argv)
  if not len(sys.argv) == 5:
    print("Usage: <quaternion label> <actual position label> <desired position label>")

  plotter = PathPlot(Reader(), *sys.argv[2:])
  while True:
    plotter.update()
