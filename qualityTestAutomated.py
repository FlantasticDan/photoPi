# automatically takes an identical photo with each encoder

# import APIs for piCamera and timings
from time import sleep
from picamera import PiCamera

# define camera as the device on CSI port 0
camera = PiCamera()

# create tuple of the encoders
imgFormat = ("jpeg", "png", "bmp", "yuv", "rgb", "bgr")

# set initial camera settings
camera.resolution = (3280, 2464)
camera.meter_mode = 'spot'
camera.image_denoise = False

# activate camera and hold for metering
camera.start_preview()
sleep(2)

# control for noise and lock exposure
if camera.iso > 400:
    camera.iso = 400
    sleep(2)
    camera.exposure_mode = 'off'
else:
    camera.exposure_mode = 'off'

# white balance calibration
camera.awb_mode = "auto"
sleep(0.5)
whiteBal = camera.awb_gains
camera.awb_mode = "off"
sleep(0.5)
camera.awb_gains = whiteBal

# query user
imgName = input("File Name:")

# inform user of current settings
print("piCamera will take " + str(len(imgFormat)) + " images named " + \
    imgName + " with the following camera settings...")
print("Exposure Speed:")
print(camera.exposure_speed)
print("Digital Gain:")
print(camera.digital_gain)
print("Analog Gain:")
print(camera.analog_gain)
print("White Balance Gain:")
print(camera.awb_gains)
print("ISO:")
print(camera.iso)

# capture loop
for x in imgFormat:
    fileName = imgName + "_" + x
    camera.capture(fileName, format=x)
    print(fileName + "." + x + " has been saved.")
    if x == "jpeg":  # jpeg bayer exception
        fileNameBayer = imgName + "_bayer"
        camera.capture(fileNameBayer, format=x, bayer=True)
        print(fileNameBayer + "." + x + " has been saved.")

camera.stop_preview()
print("All images saved.")
