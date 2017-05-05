#!/usr/bin/env python3
import argparse
from plot_lib import Plotter

parser = argparse.ArgumentParser(description="Tool for continuously plotting data",
                                 argument_default=argparse.SUPPRESS)


parser.add_argument("input_type", choices=("socket", "serial", "pipe"), help="method for passing data to the plotter (socket, serial, pipe)")
parser.add_argument("--ring_length", type=int, default=1000, help="Number of data points to plot for each package type (x axis width)")

parser.add_argument("--serial_port", type=str, help="path to serial device")
parser.add_argument("--baudrate", type=int, help="baudrate for serial port")

parser.add_argument("--remote", type=str, help="address of remote socket")
parser.add_argument("--port", type=int, help="remote sockets port")

parser.add_argument("--labels", nargs="*", default=list, help="pre determined labels to plot")

args = parser.parse_args()
print(args)

# Start plotter with data over socket connection
if args.input_type == "socket":
  if not hasattr(args, "remote") or not hasattr(args, "port"):
    parser.error("input_type=socket requires --remote and --port")
    exit(1)
  import socket_reader
  reader = socket_reader.Reader(host=args.remote, port=args.port)
  plotter = Plotter(reader=reader, ringLength=args.ring_length, labels=[])

# Start plotter with data over serial connection
elif args.input_type == "serial":
  if not hasattr(args, "baudrate") or not hasattr(args, "port"):
    parser.error("input_type=serial requires --baudrate and --port")
    exit(1)
  import serial_reader
  reader = serial_reader.Reader(port=args.port, baudrate=args.baudrate)
  plotter = Plotter(reader=reader, ringLength=args.ring_length, labels=[])

# Start plotter with data through pipe
else:
  import pipe_reader
  reader = pipe_reader.Reader()
  plotter = Plotter(reader=reader, ringLength=args.ring_length, labels=[])

while True:
  plotter.update()
