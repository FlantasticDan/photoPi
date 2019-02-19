# capture a sequence of images with constant exposure

# import necessary packages
import os
import datetime
from time import sleep
import picamera

# calibrate camera
camera = picamera.PiCamera()
camera.resolution = (3280, 2464)
camera.meter_mode = 'spot'
camera.image_denoise = False

# sets constant exposure for the camera based on a given ISO
def cameraCalibration(setISO=100):
    # initialize camera
    camera.start_preview()
    camera.iso = int(setISO)

    # lock exposure and white balance
    camera.exposure_mode = 'auto'
    camera.awb_mode = "auto"
    sleep(2)
    camera.exposure_mode = 'off'
    sleep(0.5)
    whiteBal = camera.awb_gains
    camera.awb_mode = "off"
    sleep(0.5)
    camera.awb_gains = whiteBal

    # close preview
    camera.stop_preview()

# prints current camera settings to the console
def printCameraSettings():
    print("Exposure Speed: " + str(camera.exposure_speed * 0.000001))
    print("Digital Gain: " + str(camera.digital_gain))
    print("Analog Gain: " + str(camera.analog_gain))
    print("White Balance Gain: " + str(camera.awb_gains))
    print("ISO: " + str(camera.iso))

# inital exposure
cameraCalibration()
printCameraSettings()

# confirm exposure settings
while True:
    print("Enter '0' to use the current settings.")
    exposureCheck = input("New ISO: ")
    if exposureCheck == "0":
        break
    else:
        cameraCalibration(exposureCheck)
        printCameraSettings()

# query user
fileName = input("File Name: ")
imgFormat = input("Image Format [jpeg/png/bmp/yuv/rgb/bgr]: ")
originalCount = input("Sequence Lenth (in images): ")
delay = input("Image Delay (in seconds): ")

# create workspace
os.mkdir(fileName, 0o777)
directory = fileName + "/"
imgName = directory + fileName + "_{counter:03d}." + imgFormat

# save settings reference file
settingsFile = open(directory + fileName + "_settings.txt", "w+")
settingsFile.write(str(datetime.datetime.now()))
settingsFile.write("\n" + "Exposure Speed: ")
settingsFile.write(str(camera.exposure_speed * 0.000001))
settingsFile.write("\n" + "Digital Gain: " + str(camera.digital_gain))
settingsFile.write("\n" + "Analog Gain: " + str(camera.analog_gain))
settingsFile.write("\n" + "White Balance Gain: " + str(camera.awb_gains))
settingsFile.write("\n" + "ISO: " + str(camera.iso))
settingsFile.close()

# capture inital sequence
for i in enumerate(camera.capture_continuous(imgName, format=imgFormat)):
    truePhoto = i[0] + 1
    print("Image " + str(truePhoto) + " captured.")
    if truePhoto == int(originalCount):
        break
