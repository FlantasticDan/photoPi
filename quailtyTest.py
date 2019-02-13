# takes the same photo with various encodings to compare quality

# import APIs for piCamera and timings
from time import sleep
from picamera import piCamera

# define camera as the device on CSI port 0
camera = piCamera()
