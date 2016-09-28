import sys
import socket
import time
import serial

if len(sys.argv) < 2:
    print("Usage: <server hostname>, <port (optional)>")
    sys.exit()

hostName = sys.argv[1]
if '.local' in hostName:
    hostIp = socket.gethostbyname_ex(hostName)[2][0]
else:
    hostIp = sys.argv[1]

if len(sys.argv) > 2:
    hostPort = int(sys.argv[2])
else:
    hostPort = 50007

ser = serial.Serial('/dev/ttyAMA0', baudrate=115200)
timeNow = time.time()
# Maybe because I don't know how to properly use the serial library or because the hardware I have been working with was
# acting out, this is necessary.
while True:
    try:
        read = ser.read(1).decode()
        if read == '\n':
            break
    except UnicodeDecodeError:
        pass
    if time.time() - timeNow > 0.1:
        print('Resetting connection')
        timeNow = time.time()
        ser.close()
        ser = serial.Serial('/dev/ttyAMA0', baudrate=115200)
ser.readline()

try:
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
                soc.connect((hostIp, hostPort))
                print("Connected to server")
                ser.flushInput()
                while True:
                    data = ser.readline()
                    try:
                        decodedData = data.decode()
                    except UnicodeDecodeError:
                        print(data)
                        continue
                    soc.send(bytes(str(decodedData).encode("utf-8")))

        except (ConnectionResetError, ConnectionRefusedError, BrokenPipeError):
            time.sleep(1)
            print("Waiting for server")
except KeyboardInterrupt:
    soc.close()
    ser.close()
    print("Connections closed")
    sys.exit()
