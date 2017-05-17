import sys
from visualizeQuad import QuadPlotter


def load_src(name, fpath):
    import os
    import imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), fpath))


mt = load_src('mathTools', 'quaternion/quaternion.py')


if len(sys.argv) >= 3:
  if sys.argv[1] == 'serial':
    from serial_reader import Reader
    reader = Reader(port='/dev/ttyUSB0', baudrate=57600)

  elif sys.argv[1] == 'socket':
    from socket_reader import Reader
    reader = Reader('10.0.102.2', port=50007)

  elif sys.argv[1] == 'pipe':
    from pipe_reader import Reader
    reader = Reader()

  quaLabel = sys.argv[2]
  if len(sys.argv) == 4:
    posLabel = sys.argv[3]
  else:
    posLabel = None

else:
  print("Usage <reader (socket/serial/pipe)> <quaLabel> [posLabel]")
  sys.exit()

plotter = QuadPlotter(reader=reader, quaLabel=quaLabel, posLabel=posLabel, axis=True)

while True:
  plotter.update()

# lastPlotUpdate = 0
# while True:
#   s, data, succes = reader()
#   if succes and s == label:
#     q = mt.Quaternion(*data[:4])
#     pos = data[4:7]
#     if time.time() - lastPlotUpdate > 0.03:
#       plotter.drawQuad(q, pos)
#       lastPlotUpdate = time.time()
