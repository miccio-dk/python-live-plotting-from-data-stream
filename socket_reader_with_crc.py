import socket
import numpy as np
import select


def calcCrc(s):
    crc = 0
    for c in s:
        crc ^= ord(c)
    return crc


class Reader(object):
    """ Sets up socket server that data streaming clients can connect to """
    # Use some random port

    def __init__(self, host, port, dtype=float):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Connecting to {} at {}".format(host, port))
        self.soc.connect((host, port))
        print("Connected")
        self.dtype = dtype

    def closeConnection(self):
        self.soc.close()

    def write(self, data):
        self.soc.sendall(data.encode())

    def __call__(self, label=None, raw=False):
        """ label: data group label
            raw: if true returns the data as it was read (string)
            dtype: data type that the data is converted to if raw is false """
        rawData = ''
        while True:
            # Read one byte at a time
            try:
                if select.select([self.soc], [], [], 0.5)[0]:
                    data = self.soc.recv(1)
                    char = data.decode()
                else:
                    break
            except UnicodeDecodeError:
                break
            if not char:
                # Connection closed or broken
                print("Connection lost/closed")
                self.closeConnection()
                break

            # We expect the data to be terminated with "\r\n"
            if char == '\r':
                continue
            # End of package - return result
            elif char == '\n':

                if raw:
                    # return whatever was received
                    return rawData

                try:
                    # Interpret the received data
                    if not rawData:
                        continue
                    crc = ord(rawData[-1])
                    rawData = rawData[:-1]
                    if crc == calcCrc(rawData):
                        splittedData = rawData.split(',')
                        if label is None or label == splittedData[0]:
                            return splittedData[0], np.array(list(map(self.dtype, splittedData[1:]))), True
                except ValueError:
                    return splittedData[0], splittedData[1:], False
                break
            else:
                rawData += char
        return rawData if raw else rawData, [], False


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print("Usage: <host address> <host port>")
        sys.exit()

    host = sys.argv[1]
    port = int(sys.argv[2])
    reader = Reader(host, port)

    while True:
        print(reader())
        sys.stdout.flush()
