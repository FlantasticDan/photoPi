# takes the same photo with various encodings to compare quality

# import APIs for piCamera and timings
from time import sleep
import picamera

# define camera as the device on CSI port 0
camera = picamera.piCamera()

# set initial camera settings
camera.sensor_mode = 2 # resolution set to 3280 x 2464
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
camera.awb_gains = whiteBal

# query user for settings
imgName = input("File Name:")
imgFormat = input("Image Format [jpeg/png/bmp/yuv/rgb/bgr]:")
# check for valid image format
while imgFormat != "jpeg" or imgFormat != "png" \
    or imgFormat != "bmp" or imgFormat != "yuv" or \
    imgFormat != "rgb" or imgFormat != "bgr":
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

# filename generation
fileName = imgName + "_shutter." + camera.exposure_speed + "_gains." \
    + camera.digital_gain + "." + camera.analog_gain

# capture
if imgFormat == "jpeg" and bayerBool is True:
    fileNameBayer = fileName + "_bayer"
    camera.capture(fileNameBayer, format=imgFormat, bayer=bayerBool)
camera.capture(fileName, format=imgFormat)
