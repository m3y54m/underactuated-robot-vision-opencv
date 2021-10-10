# GUI design
import tkinter as tk

# Communication with serial port
import serial
from serial.tools import list_ports

# Multi-threading
import threading

# Path of files
import pathlib

# for Image and ImageTk types
from PIL import Image, ImageTk

# Image processing
import cv2 as cv

# for time.Sleep()
# for scheduling functions using time.time()
import time

import math
import numpy as np

SRC_PATH = pathlib.Path(__file__).parent.resolve()
ICON_PATH = SRC_PATH.joinpath("icon.png")
VDO_PATH = str(SRC_PATH.parent.resolve().joinpath("assets/sample_video.mp4"))

HUE_TOLERANCE = 20
SATURATION_TOLERANCE = 120
VALUE_TOLERANCE = 120

IMAGE_WIDTH_PIXEL = 640  # in pixels
FRAME_REAL_WIDTH_CM = 215  # in centimeters

PIXEL_TO_CM_RATIO = IMAGE_WIDTH_PIXEL / FRAME_REAL_WIDTH_CM

MIN_DIAMETER_CM = 5  # in centimeters
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


def robot_control_algorithm(greenPositionCm, bluePositionCm, redPositionCm):

    ##########################################
    # Write the robot control algorithm here #
    ##########################################
    print(
        "[  VISION ] Position of joints: ({}, {}), ({}, {}), ({}, {})".format(
            int(greenPositionCm.x),
            int(greenPositionCm.y),
            int(bluePositionCm.x),
            int(bluePositionCm.y),
            int(redPositionCm.x),
            int(redPositionCm.y),
        )
    )

    # Just for test
    import random

    random.seed(time.time())

    motorSpeedA = random.uniform(-1, 1)
    motorSpeedB = random.uniform(-1, 1)

    return motorSpeedA, motorSpeedB


class RobotVisionGUI:
    # GUI main class
    def __init__(
        self,
        window,
        videoSource,
        videoFrameRate=25,
        videoAspectRatio=1.0,
        serialPortBaud=9600,
        guiUpdateInterval=40,
    ):
        # is 'Start' button clicked?
        self.isStarted = False
        # Serial port configuration
        self.portNamesList = []
        self.isAnyPortAvailable = False
        self.serialPortName = None
        self.serialPortBaud = serialPortBaud
        self.find_available_serial_ports()

        # Image processing interval might be less than GUI update interval
        self.imageProcessingInterval = 1000 // videoFrameRate
        self.videoSource = videoSource
        self.videoAspectRatio = videoAspectRatio
        self.imageProcessingManager = ImageProcessingManager(
            self.videoSource,
            self.videoAspectRatio,
            self.imageProcessingInterval,
        )

        # GUI update interval for images and other dynamic widgets
        self.guiUpdateInterval = guiUpdateInterval
        self.tkImageHeight = 250
        self.tkImageWidth = int(self.tkImageHeight * self.videoAspectRatio)
        self.originalTkImage = None
        self.processedTkImage = None

        # Joint positions in centimeters
        self.greenJointPositionCm = Point(0, 0)
        self.blueJointPositionCm = Point(0, 0)
        self.redJointPositionCm = Point(0, 0)

        self.window = window
        # Title of application window
        self.window.title("Robot Vision Application")
        # Icon of application window
        self.window.iconphoto(False, tk.PhotoImage(file=ICON_PATH))

        self.topFrame = tk.Frame(self.window, bg="#cccccc")

        self.scanButton = tk.Button(
            self.topFrame,
            text="Scan Serial Ports",
            bg="#2667ff",
            fg="#ffffff",
            border=0,
            highlightbackground="#ffffff",
            highlightthickness=2,
            activebackground="#4076ff",
            activeforeground="#ffffff",
            font=("Sans", "10", "bold"),
            command=self.scan_button_command,
        )

        # Define a tk.StringVar for storing selected item in OptionMenu
        self.selectedPort = tk.StringVar()
        # Set default value of selectedPort
        if self.isAnyPortAvailable == False:
            self.portNamesList = ["No ports available"]
        self.selectedPort.set(self.portNamesList[0])

        self.portsOptionMenu = tk.OptionMenu(
            self.topFrame, self.selectedPort, *self.portNamesList
        )

        self.portsOptionMenu.configure(
            bg="#ffffff",
            fg="#222222",
            border=0,
            highlightbackground="#aaaaaa",
            activebackground="#eeeeee",
            activeforeground="#111111",
            direction="left",
            font=("Sans", "10", "bold"),
        )
        if self.isAnyPortAvailable == False:
            self.portsOptionMenu.configure(state="disabled")

        self.startButton = tk.Button(
            self.topFrame,
            text="Start Processing",
            bg="#00a832",
            fg="#ffffff",
            border=0,
            highlightbackground="#ffffff",
            highlightthickness=2,
            activebackground="#3fcc69",
            activeforeground="#ffffff",
            font=("Sans", "10", "bold"),
            command=self.start_button_command,
        )
        if self.isAnyPortAvailable == False:
            self.startButton.configure(
                state="disabled", bg="#bbbbbb", highlightbackground="#aaaaaa"
            )

        self.greenJointLabel = tk.Label(
            self.topFrame,
            text="Green Joint: ( N/A , N/A )",
            highlightbackground="#00a832",
            highlightthickness=2,
            bg="#ffffff",
            fg="#00a832",
            padx=5,
            font=("Sans", "9", "bold"),
            anchor="w",
        )
        self.blueJointLabel = tk.Label(
            self.topFrame,
            text="Blue Joint: ( N/A , N/A )",
            highlightbackground="#2667ff",
            highlightthickness=2,
            bg="#ffffff",
            fg="#2667ff",
            padx=5,
            font=("Sans", "9", "bold"),
            anchor="w",
        )
        self.redJointLabel = tk.Label(
            self.topFrame,
            text="Red Joint: ( N/A , N/A )",
            highlightbackground="#ba0020",
            highlightthickness=2,
            bg="#ffffff",
            fg="#ba0020",
            padx=5,
            font=("Sans", "9", "bold"),
            anchor="w",
        )

        self.originalImageBox = tk.Label(
            self.topFrame,
            highlightbackground="#666666",
            highlightthickness=2,
        )

        self.originalTitle = tk.Label(
            self.topFrame,
            bg="#666666",
            fg="#ffffff",
            padx=5,
            pady=5,
            text="Original",
            font=("Sans", "9", "bold"),
            anchor="nw",
        )

        self.processedImageBox = tk.Label(
            self.topFrame,
            highlightbackground="#666666",
            highlightthickness=2,
        )

        self.processedTitle = tk.Label(
            self.topFrame,
            bg="#666666",
            fg="#ffffff",
            padx=5,
            pady=5,
            text="Processed",
            font=("Sans", "9", "bold"),
            anchor="nw",
        )

        ###############################
        ## Widgets size and position ##
        ###############################
        padding = 10
        image_height = self.tkImageHeight
        image_width = int(self.videoAspectRatio * image_height)
        control_width = 300
        button_height = 40
        label_height = 30
        menu_height = 30
        window_width = image_width * 2 + control_width + 4 * padding
        window_height = image_height + 2 * padding

        # Size of application window
        self.window.geometry("{}x{}".format(window_width, window_height))
        # Don't allow resizing in the x or y direction
        self.window.resizable(False, False)

        self.topFrame.place(x=0, y=0, width=window_width, height=window_height)

        self.originalImageBox.place(
            x=padding, y=padding, width=image_width, height=image_height
        )

        self.originalTitle.place(x=padding, y=padding)

        self.processedImageBox.place(
            x=(image_width + 2 * padding),
            y=padding,
            width=image_width,
            height=image_height,
        )

        self.processedTitle.place(
            x=(image_width + 2 * padding),
            y=padding,
        )

        self.scanButton.place(
            x=(image_width * 2 + 3 * padding),
            y=padding,
            width=control_width,
            height=button_height,
        )
        self.portsOptionMenu.place(
            x=(image_width * 2 + 3 * padding),
            y=(button_height + 2 * padding),
            width=control_width,
            height=menu_height,
        )

        self.startButton.place(
            x=(image_width * 2 + 3 * padding),
            y=(button_height + menu_height + 3 * padding),
            width=control_width,
            height=button_height,
        )
        self.greenJointLabel.place(
            x=(image_width * 2 + 3 * padding),
            y=(2 * button_height + menu_height + 4 * padding),
            width=control_width,
            height=label_height,
        )
        self.blueJointLabel.place(
            x=image_width * 2 + 3 * padding,
            y=(2 * button_height + menu_height + label_height + 5 * padding),
            width=control_width,
            height=label_height,
        )
        self.redJointLabel.place(
            x=image_width * 2 + 3 * padding,
            y=(2 * button_height + menu_height + 2 * label_height + 6 * padding),
            width=control_width,
            height=label_height,
        )

        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        # Blocking loop for GUI (Always put at the end)
        self.window.mainloop()

    def start_button_command(self):

        if self.isStarted == False:
            self.isStarted = True
            self.startButton.configure(
                bg="#ba0020",
                highlightbackground="#ffffff",
                activebackground="#cf324d",
                text="Stop Processing",
            )
            # Get desired serial port name
            self.serialPortName = self.selectedPort.get()
            # Send Serial Port configuration data to ImageProcessingManager
            self.imageProcessingManager.config_serial_port(
                self.serialPortName, self.serialPortBaud
            )
            # Start Image Processing
            self.imageProcessingManager.set_source(self.videoSource)
            self.imageProcessingManager.set_interval(self.imageProcessingInterval)
            self.imageProcessingManager.start()
            # Start updating image boxes in GUI
            # time.sleep(0.5)
            self.update_gui_loop()

        else:
            self.isStarted = False
            self.startButton.configure(
                bg="#00a832",
                highlightbackground="#ffffff",
                activebackground="#3fcc69",
                text="Start Processing",
            )
            self.imageProcessingManager.stop()

    def scan_button_command(self):
        self.portNamesList = self.find_available_serial_ports()

        if len(self.portNamesList) == 0:
            self.isAnyPortAvailable = False
            self.portNamesList = ["No ports available"]
            self.portsOptionMenu.configure(state="disabled")
            self.startButton.configure(
                state="disabled", bg="#bbbbbb", highlightbackground="#aaaaaa"
            )
        else:
            self.isAnyPortAvailable = True
            self.portsOptionMenu.configure(state="normal")
            if self.isStarted:
                self.startButton.configure(
                    bg="#ba0020",
                    highlightbackground="#ffffff",
                    activebackground="#cf324d",
                    state="normal",
                )
            else:
                self.startButton.configure(
                    bg="#00a832",
                    highlightbackground="#ffffff",
                    activebackground="#3fcc69",
                    state="normal",
                )

        self.update_option_menu(self.portNamesList)

    def find_available_serial_ports(self):
        # Clear portNames list
        portNames = []
        # Get a list of available serial ports
        portsList = list_ports.comports()
        # Sort based on port names
        portsList = sorted(portsList)

        for port in portsList:
            portNames.append(port.device)

        return portNames

    def update_option_menu(self, portNames):
        # Remove old items
        self.portsOptionMenu["menu"].delete(0, "end")
        # Add new items
        for portName in portNames:
            self.portsOptionMenu["menu"].add_command(
                label=portName, command=tk._setit(self.selectedPort, portName)
            )
        # Set default value of selectedPort
        self.selectedPort.set(portNames[0])

    def convert_cv_image_to_tk_image(self, frame, isColored):
        # In order to convert to PIL Image type should be first converted to RGB
        if isColored:
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        else:
            frame = cv.cvtColor(frame, cv.COLOR_GRAY2RGB)
        # Resize to fit the image box in GUI
        frame = cv.resize(frame, (self.tkImageWidth, self.tkImageHeight))
        # Return th ImageTk type suitable for Tkinter GUI
        return ImageTk.PhotoImage(image=Image.fromarray(frame))

    def update_gui_loop(self):
        # Update images in a kind of recursive function using Tkinter after() method
        # Get PIL ImageTk types from ImageProcessingManager for displaying in GUI
        (
            success,
            originalImage,
            processedImage,
        ) = self.imageProcessingManager.get_images()

        if success:

            try:
                # Convert CV image to PIL ImageTk in order to display in Tkinter GUI
                self.originalTkImage = self.convert_cv_image_to_tk_image(
                    originalImage, True
                )
                self.processedTkImage = self.convert_cv_image_to_tk_image(
                    processedImage, True
                )
                # Update Labels used for displaying images
                self.originalImageBox.configure(image=self.originalTkImage)
                self.processedImageBox.configure(image=self.processedTkImage)

                (
                    self.greenJointPositionCm,
                    self.blueJointPositionCm,
                    self.redJointPositionCm,
                ) = self.imageProcessingManager.get_joint_positions()

                greenString = "".join(
                    [
                        "Green Joint: ( ",
                        str(int(self.greenJointPositionCm.x)),
                        " cm , ",
                        str(int(self.greenJointPositionCm.y)),
                        " cm )",
                    ]
                )

                blueString = "".join(
                    [
                        "Blue Joint: ( ",
                        str(int(self.blueJointPositionCm.x)),
                        " cm , ",
                        str(int(self.blueJointPositionCm.y)),
                        " cm )",
                    ]
                )
                redString = "".join(
                    [
                        "Red Joint: ( ",
                        str(int(self.redJointPositionCm.x)),
                        " cm , ",
                        str(int(self.redJointPositionCm.y)),
                        " cm )",
                    ]
                )

                self.greenJointLabel.configure(text=greenString)
                self.blueJointLabel.configure(text=blueString)
                self.redJointLabel.configure(text=redString)

            except:
                # ignore errors!
                pass

        # Recursively call update_gui_loop using Tkinter after() method
        if self.imageProcessingManager.isRunning:
            self.window.after(self.guiUpdateInterval, self.update_gui_loop)

    def close_window(self):
        if self.isStarted:
            self.imageProcessingManager.stop()
        self.window.destroy()


class SerialPortManager:
    # A class for management of serial port data in a separate thread
    def __init__(self, serialPortBaud=9600):
        self.isRunning = False
        self.serialPortName = None
        self.serialPortBaud = serialPortBaud
        self.serialPort = serial.Serial()

    def set_name(self, serialPortName):
        self.serialPortName = serialPortName

    def set_baud(self, serialPortBaud):
        self.serialPortBaud = serialPortBaud

    def start(self):
        self.isRunning = True
        self.serialPortThread = threading.Thread(target=self.serial_thread_handler)
        self.serialPortThread.start()

    def stop(self):
        self.isRunning = False
        if self.serialPort.isOpen():
            self.serialPort.close()

    def serial_thread_handler(self):

        while self.isRunning:

            if not self.serialPort.isOpen():

                # Open the serial port
                self.serialPort = serial.Serial(
                    port=self.serialPortName,
                    baudrate=self.serialPortBaud,
                    bytesize=8,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                )
            else:
                try:
                    # Wait until there is data waiting in the serial buffer
                    while self.serialPort.in_waiting > 0:
                        # Read only one byte from serial port
                        serialPortByte = self.serialPort.read(1)
                        # Process incoming bytes
                        self.on_byte_received(serialPortByte)
                except:
                    # ignore errors!
                    pass

    def __del__(self):
        if self.serialPort.isOpen():
            self.serialPort.close()

    def on_byte_received(self, inputByte):
        # Print the received byte in Python terminal
        try:
            character = inputByte.decode("ascii")
        except UnicodeDecodeError:
            pass
        else:
            print(character, end="")
        pass


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
        self.serialPortBaud = 921600
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
        if self.videoCapture.isOpened():
            self.videoCapture.release()

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


if __name__ == "__main__":

    dict_video_source = {
        "camera": 0,
        "video": VDO_PATH,
        "url": "https://imageserver.webcamera.pl/rec/warszawa/latest.mp4",
    }

    videoSource = dict_video_source["video"]
    videoFrameRate = 25
    desiredAspectRatio = 1.3
    serialPortBaud = 57600
    guiUpdateInterval = 40

    # Create master Tkinter window
    # Tk() must be created here globally to avoid some errors
    window = tk.Tk()

    # Create the GUI
    gui = RobotVisionGUI(
        window,
        videoSource,
        videoFrameRate,
        desiredAspectRatio,
        serialPortBaud,
        guiUpdateInterval,
    )
