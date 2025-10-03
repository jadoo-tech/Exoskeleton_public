import time
from picamera2 import Picamera2


picam2 = Picamera2()
picam2.start()
time.sleep(2)

array = picam2.capture_array()
print(array.shape)
picam2(close)