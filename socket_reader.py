import socket
import numpy as np


class Reader(object):
    """ Sets up socket server that data streaming clients can connect to """
    # Use some random port
    def __init__(self, port=50007):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        defaultAddress = True
        while True:
            try:
                # Try to get the default port
                self.soc.bind(('', port))
                break
            except OSError:
                # The default port was not given to us by the OS. Choose new port. This can happen if the connection
                # is not closed properly. The port is usually released within a few minutes after improper termination.
                defaultAddress = False
                port += 1
        if not defaultAddress:
            print("Assigned port {:}".format(port))
        self.soc.listen(1)

        print("Waiting for client to connect")
        self.conn, addr = self.soc.accept()
        self.conn.__enter__()
        print('Connection received: {:}'.format(addr))

    def closeConnection(self):
        self.conn.close()

    def __call__(self, label=None, raw=False, dtype=float):
        """ label: data group label
            raw: if true returns the data as it was read (string)
            dtype: data type that the data is converted to if raw is false """
        rawData = ''
        while True:
            # Read one byte at a time
            char = self.conn.recv(1).decode()
            if not char:
                # Connection closed or broken
                print("Connection closed")
                self.closeConnection()
                break
            # We expect the data to be terminated with "\r\n"
            if not char == '\r':
                rawData += char
            else:
                # skip the linebreak following \r
                self.conn.recv(1)

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

if __name__ == '__main__':
    reader = Reader()

    while True:
        print(reader())