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

        self.serialPortManager = SerialPortManager(921600)
        self.get_available_serial_ports()

        self.guiUpdateInterval = 40
        # Image processing interval might be less than GUI update interval
        self.imageProcessingInterval = 40
        self.imageProcessingManager = ImageProcessingManager(
            self.imageProcessingInterval
        )

        self.window = tk.Tk()
        # Title of application window
        self.window.title("Robot Vision Application")
        # Icon of application window
        self.window.iconphoto(False, tk.PhotoImage(file=ICON_PATH))

        self.topFrame = tk.Frame(self.window, bg="#cccccc")

        self.scanButton = tk.Button(
            self.topFrame,
            text="Scan Serial Ports",
            bg="#0051ff",
            fg="#ffffff",
            border=0,
            highlightbackground="#ffffff",
            highlightthickness=2,
            activebackground="#1f7cff",
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
            highlightbackground="#0051ff",
            highlightthickness=2,
            bg="#ffffff",
            fg="#0051ff",
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

        self.recursive_update_images()

        ###############################
        ## Widgets size and position ##
        ###############################
        padding = 10
        self.imageWidth = 400
        self.imageHeight = 300
        control_width = 300
        button_height = 60
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

        self.originalTitle.place(x=padding, y=padding)

        self.processedImageBox.place(
            x=(self.imageWidth + 2 * padding),
            y=padding,
            width=self.imageWidth,
            height=self.imageHeight,
        )

        self.processedTitle.place(
            x=(self.imageWidth + 2 * padding),
            y=padding,
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
            y=(button_height + menu_height + 3 * padding),
            width=control_width,
            height=button_height,
        )
        self.greenJointLabel.place(
            x=(self.imageWidth * 2 + 3 * padding),
            y=(2 * button_height + menu_height + 4 * padding),
            width=control_width,
            height=label_height,
        )
        self.blueJointLabel.place(
            x=self.imageWidth * 2 + 3 * padding,
            y=(2 * button_height + menu_height + label_height + 5 * padding),
            width=control_width,
            height=label_height,
        )
        self.redJointLabel.place(
            x=self.imageWidth * 2 + 3 * padding,
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
            # Start Serial Port Communication
            self.serialPortManager.set_name(self.serialPortName)
            self.serialPortManager.set_baud(921600)
            self.serialPortManager.start()
            # Start Image Processing
            self.imageProcessingManager.set_source(0)
            self.imageProcessingManager.set_interval(40)
            self.imageProcessingManager.start()
            # Start updating image boxes in GUI
            self.recursive_update_images()

        else:
            self.isStarted = False
            self.startButton.configure(
                bg="#00a832",
                highlightbackground="#ffffff",
                activebackground="#3fcc69",
                text="Start Processing",
            )
            self.serialPortManager.stop()
            self.imageProcessingManager.stop()

    def scan_button_command(self):
        self.portNamesList = self.get_available_serial_ports()

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
        (
            success,
            self.originalTkImage,
            self.processedTkImage,
        ) = self.imageProcessingManager.get_tk_images()

        if success:
            # Update Labels used for displaying images
            self.originalImageBox.configure(image=self.originalTkImage)
            self.processedImageBox.configure(image=self.processedTkImage)

        # Recursively call recursive_update_images using Tkinter after() method
        if self.imageProcessingManager.isRunning:
            self.window.after(self.guiUpdateInterval, self.recursive_update_images)

    def close_window(self):
        if self.isStarted:
            self.serialPortManager.stop()
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
        self.serialPortThread = threading.Thread(target=self.thread_handler)
        self.serialPortThread.start()

    def stop(self):
        self.isRunning = False

    def thread_handler(self):

        while self.isRunning:

            if not self.serialPort.isOpen():

                self.serialPort = serial.Serial(
                    port=self.serialPortName,
                    baudrate=self.serialPortBaud,
                    bytesize=8,
                    timeout=2,
                    stopbits=serial.STOPBITS_ONE,
                )
            else:
                # Wait until there is data waiting in the serial buffer
                while self.serialPort.in_waiting > 0:
                    # Read only one byte from serial port
                    serialPortByte = self.serialPort.read(1)
                    # Process incoming bytes
                    self.main_process(serialPortByte)

        if self.serialPort.isOpen():
            self.serialPort.close()

    def __del__(self):
        if self.serialPort.isOpen():
            self.serialPort.close()

    def main_process(self, inputByte):
        # Print the received byte in Python terminal
        try:
            character = inputByte.decode("ascii")
        except UnicodeDecodeError:
            pass
        else:
            print(character, end="")


class ImageProcessingManager:
    def __init__(self, interval=40):
        self.isRunning = False
        self.videoSource = None
        self.interval = interval
        self.success = False
        self.originalFrame = None
        self.processedFrame = None
        self.originalTkImage = None
        self.processedTkImage = None
        self.tkImageWidth = 400
        self.tkImageHeight = 300
        # Open the video source
        self.videoCapture = cv2.VideoCapture()

    def set_source(self, videoSource):
        self.videoSource = videoSource

    def set_interval(self, interval):
        self.interval = interval

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

    def convert_cv_frame_to_tk_image(self, frame, isColored):
        # In order to convert to PIL Image type should be first converted to RGB
        if isColored:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        # Resize to fit the image box in GUI
        frame = cv2.resize(frame, (self.tkImageWidth, self.tkImageHeight))
        # Return th ImageTk type suitable for Tkinter GUI
        return ImageTk.PhotoImage(image=Image.fromarray(frame))

    def thread_handler(self):

        while self.isRunning:

            if not self.videoCapture.isOpened():
                self.videoCapture = cv2.VideoCapture(self.videoSource)
            else:
                self.success, self.originalFrame = self.videoCapture.read()

                if self.success:
                    # Convert CV image to PIL ImageTk in order to display in Tkinter GUI
                    self.originalTkImage = self.convert_cv_frame_to_tk_image(
                        self.originalFrame, True
                    )

                    # Process the frame
                    self.processedFrame = self.main_process(self.originalFrame)

                    # Convert CV image to PIL ImageTk in order to display in Tkinter GUI
                    self.processedTkImage = self.convert_cv_frame_to_tk_image(
                        self.processedFrame, False
                    )
                else:
                    continue

                time.sleep(self.interval / 1000)

        if self.videoCapture.isOpened():
            self.videoCapture.release()

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.videoCapture.isOpened():
            self.videoCapture.release()

    def main_process(self, inputImage):
        # Convert colored image to gray
        outputImage = cv2.cvtColor(inputImage, cv2.COLOR_BGR2GRAY)
        return outputImage


if __name__ == "__main__":
    # Create the GUI
    gui = RobotVision()
