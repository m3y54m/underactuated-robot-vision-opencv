# Image processing
import cv2 as cv

# Multi-threading
import threading

# for scheduling functions using time.time()
import time

import math
import numpy as np

# Serial Port Communications Manager
from serial_port import SerialPortManager

# Robot Control Algorithm
from robot_control import robot_control_algorithm

HUE_TOLERANCE = 20
SATURATION_TOLERANCE = 120
VALUE_TOLERANCE = 120

IMAGE_WIDTH_PIXEL = 640  # in pixels
FRAME_REAL_WIDTH_CM = 215  # in centimeters

PIXEL_TO_CM_RATIO = IMAGE_WIDTH_PIXEL / FRAME_REAL_WIDTH_CM

MIN_DIAMETER_CM = 7  # in centimeters
MAX_DIAMETER_CM = 15  # in centimeters
GREEN_BLUE_LINK_LENGTH_CM = 30  # in centimeters

MIN_CONTOUR_AREA = math.pow((MIN_DIAMETER_CM / 2) * PIXEL_TO_CM_RATIO, 2) * math.pi
MAX_CONTOUR_AREA = math.pow((MAX_DIAMETER_CM / 2) * PIXEL_TO_CM_RATIO, 2) * math.pi

BGR_RED = (0, 0, 255)
BGR_BLUE = (255, 0, 0)
BGR_GREEN = (0, 255, 0)
BGR_WHITE = (255, 255, 255)


class Hsv:
    def __init__(self, hue=0, saturation=0, value=0):
        self.hue = hue
        self.saturation = saturation
        self.value = value


CALIBRATED_HSV_RED = Hsv(178, 243, 175)
CALIBRATED_HSV_BLUE = Hsv(113, 189, 115)
CALIBRATED_HSV_GREEN = Hsv(55, 157, 135)


class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class ImageProcessingManager:
    def __init__(
        self,
        videoSource,
        videoAspectRatio=1.0,
        intervalMilliseconds=40,
    ):

        self.isRunning = False
        self.videoSource = videoSource
        self.videoAspectRatio = videoAspectRatio
        self.intervalMilliseconds = intervalMilliseconds
        self.success = False
        self.originalImage = None
        self.processedImage = None

        # Joint positions in centimeters
        self.greenJointPositionCm = Point(0, 0)
        self.blueJointPositionCm = Point(0, 0)
        self.redJointPositionCm = Point(0, 0)

        # Motor speeds are float numbers in range (-1, 1)
        # negative speed means reverse direction
        self.motorSpeedA = 0
        self.motorSpeedB = 0

        self.serialPortName = None
        self.serialPortBaud = 9600
        self.serialPortManager = SerialPortManager(self.serialPortBaud)

        # Open the video source
        self.videoCapture = cv.VideoCapture()

    def set_source(self, videoSource):
        self.videoSource = videoSource

    def set_interval(self, interval):
        self.intervalMilliseconds = interval

    def config_serial_port(self, portName, baudRate):
        self.serialPortName = portName
        self.serialPortBaud = baudRate

    def get_joint_positions(self):
        return (
            self.greenJointPositionCm,
            self.blueJointPositionCm,
            self.redJointPositionCm,
        )

    def get_images(self):
        return self.success, self.originalImage, self.processedImage

    def start(self):
        self.isRunning = True
        # Start Serial Port Communication
        self.serialPortManager.set_name(self.serialPortName)
        self.serialPortManager.set_baud(self.serialPortBaud)
        self.serialPortManager.start()
        # Start Video Capture Thread
        self.videoCaptureThread = threading.Thread(target=self.image_thread_handler)
        self.videoCaptureThread.start()

    def stop(self):
        self.isRunning = False
        self.serialPortManager.stop()

    def image_thread_handler(self):

        while self.isRunning:

            # Do processing on captured frame in certain intervals
            if time_ms() % self.intervalMilliseconds == 0:

                if not self.videoCapture.isOpened():
                    self.videoCapture = cv.VideoCapture(self.videoSource)
                else:
                    success, frame = self.videoCapture.read()

                    self.success = success and frame.all != None

                    if self.success:
                        # Correct aspect ratio of frame by cropping
                        self.originalImage = crop_image(frame, self.videoAspectRatio)

                        ##################################
                        #  Main Image Processing Routine #
                        ##################################
                        self.processedImage = self.main_image_processing(
                            self.originalImage
                        )

                    else:
                        continue

    # Release the video source when the object is destroyed
    def __del__(self):
        self.serialPortManager.stop()
        if self.videoCapture.isOpened():
            self.videoCapture.release()

    def main_image_processing(self, inputImage):

        success, greenCenter, blueCenter, redCenter, outputImage = find_join_positions(
            inputImage
        )

        if success:

            scalingRatio = (
                math.sqrt(
                    math.pow(blueCenter.x - greenCenter.x, 2)
                    + math.pow(blueCenter.y - greenCenter.y, 2)
                )
                / GREEN_BLUE_LINK_LENGTH_CM
            )

            # Convert units pixel position units into ground truth centimeters
            # the Green point is considered as the origin of our coordinate system
            blueCmX = (1 / scalingRatio) * (blueCenter.x - greenCenter.x)
            blueCmY = -(1 / scalingRatio) * (blueCenter.y - greenCenter.y)
            redCmX = (1 / scalingRatio) * (redCenter.x - greenCenter.x)
            redCmY = -(1 / scalingRatio) * (redCenter.y - greenCenter.y)

            self.blueJointPositionCm = Point(blueCmX, blueCmY)
            self.redJointPositionCm = Point(redCmX, redCmY)

            # Give joint positions to the Robot Control Algorithm and get the motor speeds
            self.motorSpeedA, self.motorSpeedB = robot_control_algorithm(
                self.greenJointPositionCm,
                self.blueJointPositionCm,
                self.redJointPositionCm,
            )

            # Send speed of motors to Arduino board
            self.send_motor_speeds(self.motorSpeedA, self.motorSpeedB)

        return outputImage

    def send_motor_speeds(self, speedA, speedB):
        # speeds must be normalized and saturated between -1.0 and 1.0
        if speedA > 1.0:
            speedA = 1.0

        if speedA < -1.0:
            speedA = -1.0

        if speedB > 1.0:
            speedB = 1.0

        if speedB < -1.0:
            speedB = -1.0

        # Create a 3-byte packet which is defined in Arduino code
        cmdPacket = [0xFF, 0, 0]
        # 0xFF or 255 is reserved for start of packet byte
        # so the speed bytes value range is (0, 254)
        cmdPacket[1] = map_number(int(speedA * 255), -255, 255, 0, 254)
        cmdPacket[2] = map_number(int(speedB * 255), -255, 255, 0, 254)

        # Send cmdPacket to serial port
        try:
            if (
                self.serialPortManager.serialPort.isOpen()
                and self.serialPortManager.isRunning
            ):
                self.serialPortManager.serialPort.write(bytearray(cmdPacket))
        except:
            # ignore errors
            pass


def time_ms():
    # Get time in milliseconds
    return int(time.time() * 1000)


def crop_image(inputImage, desiredAspectRatio):

    imageHeight = inputImage.shape[0]
    imageWidth = inputImage.shape[1]
    currentAspectRatio = imageWidth / imageHeight

    if currentAspectRatio > desiredAspectRatio:

        desiredWidth = int(imageHeight * desiredAspectRatio)
        diff = int((imageWidth - desiredWidth) / 2)
        croppedImage = inputImage[:, int(diff) : int(imageWidth - diff)]

    elif currentAspectRatio < desiredAspectRatio:

        desiredHeight = int(imageWidth / desiredAspectRatio)
        diff = int((imageHeight - desiredHeight) / 2)
        croppedImage = inputImage[int(diff) : int(imageHeight - diff), :]

    else:
        croppedImage = inputImage

    return croppedImage


def filter_color(hsvImage, colorNameToFilter):

    if colorNameToFilter == "green":

        baseHue = CALIBRATED_HSV_GREEN.hue
        baseSaturation = CALIBRATED_HSV_GREEN.saturation
        baseValue = CALIBRATED_HSV_GREEN.value

    elif colorNameToFilter == "blue":

        baseHue = CALIBRATED_HSV_BLUE.hue
        baseSaturation = CALIBRATED_HSV_BLUE.saturation
        baseValue = CALIBRATED_HSV_BLUE.value

    elif colorNameToFilter == "red":

        baseHue = CALIBRATED_HSV_RED.hue
        baseSaturation = CALIBRATED_HSV_RED.saturation
        baseValue = CALIBRATED_HSV_RED.value

    else:
        pass

    hueMin = baseHue - HUE_TOLERANCE
    saturationMin = baseSaturation - SATURATION_TOLERANCE
    valueMin = baseValue - VALUE_TOLERANCE

    hueMax = baseHue + HUE_TOLERANCE
    saturationMax = baseSaturation + SATURATION_TOLERANCE
    valueMax = baseValue + VALUE_TOLERANCE

    if hueMin < 0:
        hueMin = 0

    if hueMax > 180:
        hueMax = 180

    if saturationMin < 0:
        saturationMin = 0

    if saturationMax > 255:
        saturationMax = 255

    if valueMin < 0:
        valueMin = 0

    if valueMax > 255:
        valueMax = 255

    filteredImage = cv.inRange(
        hsvImage, (hueMin, saturationMin, valueMin), (hueMax, saturationMax, valueMax)
    )

    # red color covers some hues around 0 and some around 180
    # so two hue ranges is consired for filtering red color
    if colorNameToFilter == "red":

        hueMin2 = 0
        hueMax2 = 0

        if hueMin < 0:
            hueMin2 = 180 + hueMin
            hueMax2 = 180

        if hueMax > 180:
            hueMin2 = 0
            hueMax2 = hueMax - 180

        filteredImage2 = cv.inRange(
            hsvImage,
            (hueMin2, saturationMin, valueMin),
            (hueMax2, saturationMax, valueMax),
        )
        filteredImage = cv.bitwise_or(filteredImage, filteredImage2)

    kernel = np.ones((5, 5), np.uint8)
    # remove some noise
    filteredImage = cv.erode(filteredImage, kernel, iterations=3)
    filteredImage = cv.dilate(filteredImage, kernel, iterations=3)

    return filteredImage


def find_center(filteredImage):

    success = False
    center = Point(0, 0)

    contours, hierarchy = cv.findContours(
        filteredImage, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE
    )

    for contour in contours:

        moment = cv.moments(contour)

        if moment["m00"] != 0:

            x = int(moment["m10"] / moment["m00"])
            y = int(moment["m01"] / moment["m00"])

            contourArea = cv.contourArea(contour)

            if (contourArea > MIN_CONTOUR_AREA) and (contourArea < MAX_CONTOUR_AREA):

                success = True
                center = Point(x, y)

    return success, center


def find_join_positions(inputImage):

    success = False

    greenCenter = Point(0, 0)
    blueCenter = Point(0, 0)
    redCenter = Point(0, 0)

    greenCenterReady = False
    blueCenterReady = False
    redCenterReady = False

    hsvImage = cv.cvtColor(inputImage, cv.COLOR_BGR2HSV)

    # filter green color
    filteredGreen = filter_color(hsvImage, "green")
    # filter red color
    filteredBlue = filter_color(hsvImage, "blue")
    # filter red color
    filteredRed = filter_color(hsvImage, "red")

    # get green color coordinates
    greenCenterReady, greenCenter = find_center(filteredGreen)
    # get blue color coordinates
    blueCenterReady, blueCenter = find_center(filteredBlue)
    # get red color coordinates
    redCenterReady, redCenter = find_center(filteredRed)

    # Create a blank image
    processedImage = np.zeros(inputImage.shape, dtype=np.uint8)

    if greenCenterReady:
        # draw green circle
        processedImage = cv.circle(
            processedImage,
            (greenCenter.x, greenCenter.y),
            int(MAX_DIAMETER_CM * PIXEL_TO_CM_RATIO / 2),
            BGR_GREEN,
            -1,
        )

    if blueCenterReady:
        # draw blue circle
        processedImage = cv.circle(
            processedImage,
            (blueCenter.x, blueCenter.y),
            int(MAX_DIAMETER_CM * PIXEL_TO_CM_RATIO / 2),
            BGR_BLUE,
            -1,
        )

    if redCenterReady:
        # draw red circle
        processedImage = cv.circle(
            processedImage,
            (redCenter.x, redCenter.y),
            int(MAX_DIAMETER_CM * PIXEL_TO_CM_RATIO / 2),
            BGR_RED,
            -1,
        )

    if greenCenterReady and blueCenterReady:
        # draw line between green and blue points
        processedImage = cv.line(
            processedImage,
            (greenCenter.x, greenCenter.y),
            (blueCenter.x, blueCenter.y),
            BGR_WHITE,
            5,
        )

    if blueCenterReady and redCenterReady:
        # draw line between blue and red points
        processedImage = cv.line(
            processedImage,
            (blueCenter.x, blueCenter.y),
            (redCenter.x, redCenter.y),
            BGR_WHITE,
            5,
        )

    if greenCenterReady and blueCenterReady and redCenterReady:
        success = True

    return success, greenCenter, blueCenter, redCenter, processedImage


def map_number(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)
