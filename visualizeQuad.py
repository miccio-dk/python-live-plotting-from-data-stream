import imp
import sys
import time
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

mt = imp.load_source('mathTools', 'quaternion/quaternion.py')

if len(sys.argv) > 2:
    if sys.argv[1] == 'serial':
        from serial_reader import Reader
        reader = Reader(port='/dev/ttyUSB0', baudrate=115200)

    elif sys.argv[1] == 'socket':
        from socket_reader import Reader
        reader = Reader('10.0.2.50', port=50007)

    elif sys.argv[1] == 'pipe':
        from pipe_reader import Reader
        reader = Reader()

    label = sys.argv[2]
else:
    print("Usage <reader (socket/serial/pipe)> <quaternion label>")
    sys.exit()


def press(event):
    if event.key == 'q':
        plt.close(event.canvas.figure)
        sys.exit()


fig = plt.figure()
fig.canvas.mpl_connect('key_press_event', press)
axLive = fig.add_subplot(1, 1, 1, aspect='equal', projection='3d')
lines = [axLive.plot([], [], [], 'r', linewidth=3)[0],
         axLive.plot([], [], [], 'g', linewidth=3)[0],
         axLive.plot([], [], [], 'b', linewidth=3)[0]]
axLive.set_xlabel("x")
axLive.set_ylabel("y")
axLive.set_zlabel("z")

axLive.set_xlim3d(-1, 1)
axLive.set_ylim3d(-1, 1)
axLive.set_zlim3d(-1, 1)


def drawQuad(q, line):
    lineX = q.rotateVectors(np.array([[-0.3,    0, 0], [0.3,   0,   0]]).T)
    lineY = q.rotateVectors(np.array([[   0, -0.3, 0], [  0, 0.3,   0]]).T)
    lineZ = q.rotateVectors(np.array([[   0,    0, 0], [  0,   0, 0.3]]).T)

    lines[0].set_xdata(lineX[0, :])
    lines[0].set_ydata(lineX[1, :])
    lines[0].set_3d_properties(lineX[2, :])
    lines[1].set_xdata(lineY[0, :])
    lines[1].set_ydata(lineY[1, :])
    lines[1].set_3d_properties(lineY[2, :])
    lines[2].set_xdata(lineZ[0, :])
    lines[2].set_ydata(lineZ[1, :])
    lines[2].set_3d_properties(lineZ[2, :])

lastPlotUpdate = 0
while True:
    s, data = reader(label=label)

    q = mt.Quaternion(*data)
    if time.time() - lastPlotUpdate > 0.03:
        drawQuad(q, lines)
        plt.pause(0.00001)
        lastPlotUpdate = time.time()
