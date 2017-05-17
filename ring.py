import numpy as np


class Ring(object):
  def __init__(self, nY, length):
    self.nY = nY
    self.length = length
    self.reset()

  def update(self, val):
    self.xs[self.tail] = self.xs[self.head] + 1
    self.head = self.tail
    self.tail = (self.tail + 1) % self.length
    self.yData[:, self.head] = val
    if val.max() > self.maxY:
      self.maxY = val.max()
    if val.min() < self.minY:
      self.minY = val.min()

  def reset(self):
    self.yData = np.zeros((self.nY, self.length))
    # Make sure y-axis limits will be set correctly
    # This is a little dirty but it does what it is supposed to in a very simple way.
    # Alternatively all columns in yData could be set equal to the first data point received after a reset
    self.yData[:] = None
    self.xs = np.zeros(self.length)
    self.count = 0
    self.minY = float('inf')
    self.maxY = -float('inf')
    self.head = 0
    self.tail = -1
    self.lostTail = np.zeros(self.nY)

  def looseTail(self):
    self.lostTail = self.yData[:, self.tail].copy()
    self.yData[:, self.tail] = None

  def fixTail(self):
    self.yData[:, self.tail] = self.lostTail
