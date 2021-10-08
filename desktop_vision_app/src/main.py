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
import cv2

# for time.Sleep()
import time

SRC_PATH = pathlib.Path(__file__).parent.resolve()
ICON_PATH = SRC_PATH.joinpath("icon.png")


class RobotVision:
    # GUI main class
    def __init__(self):

        self.portNamesList = []
        self.isAnyPortAvailable = False
        self.isStarted = False
        self.serialPortName = None

        self.serialPortManager = SerialPortManager()
        self.get_available_serial_ports()

        self.updateInterval = 40
        self.imageProcessingManager = ImageProcessingManager(0, self.updateInterval)

        self.window = tk.Tk()
        # Title of application window
        self.window.title("Robot Vision Application")
        # Icon of application window
        self.window.iconphoto(False, tk.PhotoImage(file=ICON_PATH))

        self.topFrame = tk.Frame(self.window)

        self.scanButton = tk.Button(
            self.topFrame,
            text="Scan serial ports",
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

        if self.isAnyPortAvailable == False:
            self.portsOptionMenu.configure(state="disabled")

        self.startButton = tk.Button(
            self.topFrame,
            text="Start processing",
            command=self.start_button_command,
        )
        if self.isAnyPortAvailable == False:
            self.startButton.configure(state="disabled")

        self.greenJointLabel = tk.Label(
            self.topFrame, text="Green join position", anchor="w"
        )
        self.blueJointLabel = tk.Label(
            self.topFrame, text="Blue joint position", anchor="w"
        )
        self.redJointLabel = tk.Label(
            self.topFrame, text="Red joint position", anchor="w"
        )

        self.originalImageBox = tk.Label(self.topFrame)
        self.processedImageBox = tk.Label(self.topFrame)

        self.recursive_update_images()

        ###############################
        ## Widgets size and position ##
        ###############################
        padding = 10
        self.imageWidth = 400
        self.imageHeight = 300
        control_width = 300
        button_height = 50
        label_height = 30
        menu_height = 40
        window_width = self.imageWidth * 2 + control_width + 4 * padding
        window_height = self.imageHeight + 2 * padding

        # Size of application window
        self.window.geometry("{}x{}".format(window_width, window_height))
        # Don't allow resizing in the x or y direction
        self.window.resizable(False, False)

        self.topFrame.place(x=0, y=0, width=window_width, height=window_height)

        self.originalImageBox.place(
            x=padding, y=padding, width=self.imageWidth, height=self.imageHeight
        )
        self.processedImageBox.place(
            x=(self.imageWidth + 2 * padding),
            y=padding,
            width=self.imageWidth,
            height=self.imageHeight,
        )

        self.scanButton.place(
            x=(self.imageWidth * 2 + 3 * padding),
            y=padding,
            width=control_width,
            height=button_height,
        )
        self.portsOptionMenu.place(
            x=(self.imageWidth * 2 + 3 * padding),
            y=(button_height + 2 * padding),
            width=control_width,
            height=menu_height,
        )

        self.startButton.place(
            x=(self.imageWidth * 2 + 3 * padding),
            y=(button_height + menu_height + 4 * padding),
            width=control_width,
            height=button_height,
        )
        self.greenJointLabel.place(
            x=(self.imageWidth * 2 + 3 * padding),
            y=(2 * button_height + menu_height + 5 * padding),
            width=control_width,
            height=label_height,
        )
        self.blueJointLabel.place(
            x=self.imageWidth * 2 + 3 * padding,
            y=(2 * button_height + menu_height + label_height + 6 * padding),
            width=control_width,
            height=label_height,
        )
        self.redJointLabel.place(
            x=self.imageWidth * 2 + 3 * padding,
            y=(2 * button_height + menu_height + 2 * label_height + 7 * padding),
            width=control_width,
            height=label_height,
        )

        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        # Blocking loop for GUI (Always put at the end)
        self.window.mainloop()

    def start_button_command(self):

        if self.isStarted == False:
            self.isStarted = True
            self.startButton.configure(text="Stop processing")
            self.serialPortName = self.selectedPort.get()
            self.serialPortManager.set_name(self.serialPortName)
            self.serialPortManager.start()
            self.imageProcessingManager.set_source(0)
            self.imageProcessingManager.start()
            self.recursive_update_images()
        else:
            self.isStarted = False
            self.startButton.configure(text="Start processing")
            self.serialPortManager.stop()
            self.imageProcessingManager.stop()

    def scan_button_command(self):
        self.portNamesList = self.get_available_serial_ports()

        if len(self.portNamesList) == 0:
            self.isAnyPortAvailable = False
            self.portNamesList = ["No ports available"]
            self.portsOptionMenu.configure(state="disabled")
            self.startButton.configure(state="disabled")
        else:
            self.isAnyPortAvailable = True
            self.portsOptionMenu.configure(state="normal")
            self.startButton.configure(state="normal")

        self.update_option_menu(self.portNamesList)

    def get_available_serial_ports(self):
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

    def recursive_update_images(self):
        # Update images in a kind of recursive function using Tkinter after() method
        # Get PIL ImageTk types from ImageProcessingManager for displaying in GUI
        success, self.originalTkImage,  self.processedTkImage = self.imageProcessingManager.get_tk_images()
        
        if success:
            # Update Labels used for displaying images
            self.originalImageBox.configure(image=self.originalTkImage)
            self.processedImageBox.configure(image=self.processedTkImage)
            
        # Recursively call recursive_update_images using Tkinter after() method
        if self.imageProcessingManager.isRunning:
            self.window.after(self.updateInterval, self.recursive_update_images)

    def close_window(self):
        if self.isStarted:
            self.serialPortManager.stop()
            self.imageProcessingManager.stop()
        self.window.destroy()


class SerialPortManager:
    # A class for management of serial port data in a separate thread
    def __init__(self):
        self.isRunning = False
        self.serialPortName = None
        self.serialPortBaud = 921600

    def set_name(self, serialPortName):
        self.serialPortName = serialPortName

    def start(self):

        self.isRunning = True
        self.serialPortThread = threading.Thread(target=self.thread_handler)
        self.serialPortThread.start()

    def stop(self):
        self.isRunning = False
        self.serialPortThread.join()

    def thread_handler(self):

        serialPort = serial.Serial(
            port=self.serialPortName,
            baudrate=self.serialPortBaud,
            bytesize=8,
            timeout=2,
            stopbits=serial.STOPBITS_ONE,
        )

        while self.isRunning:
            # Wait until there is data waiting in the serial buffer
            while serialPort.in_waiting > 0:
                # Read only one byte from serial port
                serialPortByte = serialPort.read(1)
                # Print the received byte in Python terminal
                try:
                    character = serialPortByte.decode("ascii")
                except UnicodeDecodeError:
                    pass
                else:
                    print(character, end="")

        serialPort.close()


class ImageProcessingManager:
    def __init__(self, videoSource=0, updateInterval=40):
        self.isRunning = False
        self.videoSource = videoSource
        self.updateInterval = updateInterval
        # Open the video source
        self.videoCapture = cv2.VideoCapture(self.videoSource)

        self.success = False
        self.originalFrame = None
        self.processedFrame = None
        self.originalTkImage = None
        self.processedTkImage = None
        self.tkImageWidth = 400
        self.tkImageHeight = 300

    def set_source(self, videoSource):
        self.videoSource = videoSource

    def get_frame(self):
        return self.success, self.originalFrame

    def get_tk_images(self):
        return self.success, self.originalTkImage, self.processedTkImage

    def start(self):
        self.isRunning = True
        self.videoCaptureThread = threading.Thread(target=self.thread_handler)
        self.videoCaptureThread.start()

    def stop(self):
        self.isRunning = False
        if self.videoCapture.isOpened():
            self.videoCapture.release()
        self.videoCaptureThread.join()

    def convert_cv_frame_to_tk_image(self, frame):
        # In order to convert to PIL Image type should be first converted to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (self.tkImageWidth, self.tkImageHeight))
        return ImageTk.PhotoImage(image=Image.fromarray(frame))

    def thread_handler(self):

        self.videoCapture = cv2.VideoCapture(self.videoSource)

        while self.isRunning:
            if self.videoCapture.isOpened():

                self.success, self.originalFrame = self.videoCapture.read()


                if self.success:
                    # In order to convert to PIL Image type should be first converted to RGB
                    self.frame = cv2.cvtColor(self.originalFrame, cv2.COLOR_BGR2RGB)
                    self.frame = cv2.resize(self.frame, (self.tkImageWidth, self.tkImageHeight))
                    self.originalTkImage = ImageTk.PhotoImage(image=Image.fromarray(self.frame))

                    # Process the frame
                    self.processedFrame = self.main_process(self.originalFrame)

                    # In order to convert to PIL Image type should be first converted to RGB
                    self.frame = cv2.cvtColor(self.processedFrame, cv2.COLOR_GRAY2RGB)
                    self.frame = cv2.resize(self.frame, (self.tkImageWidth, self.tkImageHeight))
                    self.processedTkImage = ImageTk.PhotoImage(image=Image.fromarray(self.frame))
                else:
                    print("[MyVideoCapture] stream end:", self.videoSource)
                    continue

                time.sleep(self.updateInterval / 1000)

        if self.videoCapture.isOpened():
            self.videoCapture.release()

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.videoCapture.isOpened():
            self.videoCapture.release()

    def main_process(self, inputImage):
        outputImage = cv2.cvtColor(inputImage, cv2.COLOR_BGR2GRAY)
        return outputImage

if __name__ == "__main__":
    # cap = ImageProcessingManager(0)
    # Create the GUI
    gui = RobotVision()
