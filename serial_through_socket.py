import sys
assert sys.version_info >= (3,0)

import socket
import serial
import time
import select


class serialHandler(object):
  def __init__(self, port, baud):
    print("Trying to connect to device over serial port {:} at baudrate {:}".format(port, baud))
    self.ser = serial.Serial(port=port, baudrate=baud)

  def read(self, data):
    available = self.ser.inWaiting()
    if available:
      data[0] = self.ser.readline()
      while self.ser.inWaiting():
        self.ser.readline()
      return 1
    else:
      return 0

  def write(self, data):
    self.ser.write(data)
    # self.ser.flush()

  def close(self):
    self.ser.close()


class socketHandler(object):
  def __init__(self, ip, port):
    self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    defaultAddress = True
    while True:
      try:
        # Try to get the default port
        self.soc.bind((ip, port))
        break
      except OSError:
        # The default port was not given to us by the OS. Choosing new port. This can
        # happen if the connection is not closed properly. The port is usually
        # released within a few minutes after improper termination.
        defaultAddress = False
        port += 1
    if not defaultAddress:
      print("Assigned port {:}".format(port))
    print("Waiting for clients to connect at {}".format(self.soc.getsockname()))
    self.soc.listen(1)
    self.receiveConnection()

  def receiveConnection(self):
    self.conn, self.addr = self.soc.accept()

  def read(self, data):
    s = []
    while True:
      available = select.select([self.conn], [], [], 0.0)[0]
      if available:
        newestByte = self.conn.recv(1)
        if newestByte == "\r":
          continue
        elif newestByte == "\n":
          break
        else:
          s.append(newestByte)
      else:
        break
    data[0] = "".join(s)
    return True

  def write(self, data):
    try:
      self.conn.sendall(data)
    except ConnectionResetError:
      self.receiveConnection()

  def close(self):
    self.soc.close()


if __name__ == "__main__":
  import sys
  ip = ''
  port = 50007
  serPort = "/dev/serial0"
  serBaud = 115200
  if len(sys.argv) == 3:
    ip = sys.argv[1]
    port = int(sys.argv[2])
  elif len(sys.argv) == 5:
    ip = sys.argv[1]
    port = int(sys.argv[2])
    serPort = sys.argv[3]
    serBaud = sys.argv[4]
  elif len(sys.argv) != 1:
    print("Usage: <ip> <port> <serial port> <baudrate>\nsupply either nothing or ip and port or ip, port, serial port and baudrate")


  # Autopilot read/write
  serHandle = serialHandler(serPort, serBaud)
  # Client    read/write
  socHandle = socketHandler(ip, port)

  serData = [""]
  socData = [""]
  i = 0
  try:
    while True:
      if serHandle.read(serData):
        socHandle.write(serData[0])
      if socHandle.read(socData):
        serHandle.write(socData[0])
      time.sleep(0.001)
  except KeyboardInterrupt:
    socHandle.close()
    serHandle.close()
    print("Connections closed")
    sys.exit()

