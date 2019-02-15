# automatically takes an identical photo with each encoder

# import APIs for piCamera and timings
from time import sleep
from picamera import PiCamera
import datetime
import os

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
imgName = input("File Name: ")

# denoise enabler backdoor
if imgName == "denoise":
    camera.image_denoise = True
    print("Image Denoise Algorithm Enabled")
    imgName = input("Let's try a real File Name: ")

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

# export exposure data
pathFolder = imgName
os.mkdir(pathFolder, 0o777)
settingsFile = open(imgName + "/" + imgName + \
    "_settings.txt", "w+")
settingsFile.write(str(datetime.datetime.now()))
settingsFile.write("\n" + "Exposure Speed:" + "\n")
settingsFile.write(str(camera.exposure_speed))
settingsFile.write("\n" + "Digital Gain:" + "\n")
settingsFile.write(str(camera.digital_gain))
settingsFile.write("\n" + "Analog Gain:" + "\n")
settingsFile.write(str(camera.analog_gain))
settingsFile.write("\n" + "White Balance Gain:" + "\n")
settingsFile.write(str(camera.awb_gains))
settingsFile.write("\n" + "ISO:" + "\n")
settingsFile.write(str(camera.iso))
settingsFile.write("\n" + "Denoiser: " + "\n")
settingsFile.write(str(camera.image_denoise))
settingsFile.close()

# capture loop
for x in imgFormat:
    fileName = imgName + "_" + x
    camera.capture(imgName + "/" + fileName, format=x)
    print(fileName + "." + x + " has been saved.")
    if x == "jpeg":  # jpeg bayer exception
        fileNameBayer = imgName + "/" + imgName + "_bayer"
        camera.capture(fileNameBayer, format=x, bayer=True)
        print(fileNameBayer + "." + x + " has been saved.")

camera.stop_preview()
camera.close()
print("All images saved.")
