import numpy as np
import time

c = 0
while True:
    print("joj,{:.4f},{:.4f}".format(*np.random.randn(2)))
    c += 1
    time.sleep(0.0001)
