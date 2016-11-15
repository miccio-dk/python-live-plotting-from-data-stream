import socket
import numpy as np


class Reader(object):
    """ Sets up socket server that data streaming clients can connect to """
    # Use some random port
    def __init__(self, host, port):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Connecting to {} at {}".format(host, port))
        self.soc.connect((host, port))
        print("Connected")

    def closeConnection(self):
        self.soc.close()

    def __call__(self, label=None, raw=False, dtype=float):
        """ label: data group label
            raw: if true returns the data as it was read (string)
            dtype: data type that the data is converted to if raw is false """
        rawData = ''
        while True:
            # Read one byte at a time
            char = self.soc.recv(1).decode()
            if not char:
                # Connection closed or broken
                print("Connection closed")
                self.closeConnection()
                break
            # We expect the data to be terminated with "\r\n"
            if char == '\r':
                continue
            elif char == '\n':
                # skip the linebreak following \r
                self.soc.recv(1)

                if raw:
                    # return whatever was received
                    return rawData

                try:
                    # Interpret the received data
                    splittedData = rawData.split(',')
                    if label is None or label == splittedData[0]:
                        return splittedData[0], np.array(list(map(dtype, splittedData[1:])))
                except ValueError:
                    pass
                print(rawData)
                rawData = ''
            else:
                rawData += char

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print("Usage: <host address> <host port>")
        sys.exit()

    host = sys.argv[1]
    port = int(sys.argv[2])
    reader = Reader(host, port)

    while True:
        print(reader(raw=True))
