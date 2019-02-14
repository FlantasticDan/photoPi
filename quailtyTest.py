# takes the same photo with various encodings to compare quality

# import APIs for piCamera and timings
from time import sleep
from picamera import PiCamera

# define camera as the device on CSI port 0
camera = PiCamera()

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

# query user for settings
imgName = input("File Name:")
imgFormat = input("Image Format [jpeg/png/bmp/yuv/rgb/bgr]:")
# check for valid image format
while imgFormat != "jpeg" and imgFormat != "png" \
    and imgFormat != "bmp" and imgFormat != "yuv" and \
    imgFormat != "rgb" and imgFormat != "bgr":
    print("Invalid Image Format")
    imgFormat = input("Choose from [jpeg/png/bmp/yuv/rgb/bgr]:")
# jpeg option configuation
if imgFormat == "jpeg":
    bayerInput = input("Include RAW Bayer data w/ jpeg? [y/n]:")
    if bayerInput == "y":
        bayerBool = True
    elif bayerInput == "n":
        bayerBool = False
    else:
        print("Invalid Input")
        print("Defaulting to [n]")
        bayerBool = False

# print exposure data
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

# capture
if imgFormat == "jpeg" and bayerBool is True:
    fileNameBayer = imgName + "_bayer"
    camera.capture(fileNameBayer, format=imgFormat, bayer=bayerBool)
camera.capture(imgName, format=imgFormat)

# exit
print(imgName + "." + imgFormat + " has been saved")
camera.stop_preview()

