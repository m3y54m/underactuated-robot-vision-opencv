# GUI design
import tkinter as tk

# Communication with serial port
import serial
from serial.tools import list_ports

# Multi-threading
import threading

# Path of files
import pathlib

# Working with images
from PIL import Image, ImageTk

# Image processing
import cv2

SRC_PATH = pathlib.Path(__file__).parent.resolve()
ICON_PATH = SRC_PATH.joinpath("icon.png")


class ImageProcessing:
    pass


class SerialPort:
    def __init__(self):
        self.isOpen = False
        self.serialPortName = None
        self.serialPortBaud = 921600

    def set_name(self, serialPortName):
        self.serialPortName = serialPortName

    def open(self):
        self.isOpen = True
        self.serialPortThread = threading.Thread(target=self.thread_handler)
        self.serialPortThread.start()

    def close(self):
        self.isOpen = False
        self.serialPortThread.join()

    def thread_handler(self):

        serialPort = serial.Serial(
            port=self.serialPortName,
            baudrate=self.serialPortBaud,
            bytesize=8,
            timeout=2,
            stopbits=serial.STOPBITS_ONE,
        )

        while self.isOpen:
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


class RobotVision:
    def __init__(self):

        self.portNamesList = []
        self.isAnyPortAvailable = False
        self.isStarted = False
        self.serialPortName = None

        self.serialPort = SerialPort()

        self.get_available_serial_ports()

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

        self.selectedPort = tk.StringVar(self.topFrame)
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

        self.originalImageLabel = tk.Label(self.topFrame, bg="white")
        self.processedImageLabel = tk.Label(self.topFrame, bg="white")

        ###############################
        ## Widgets size and position ##
        ###############################
        padding = 10
        image_width = 400
        image_hight = 300
        control_width = 300
        button_height = 50
        label_height = 30
        menu_height = 40
        window_width = image_width * 2 + control_width + 4 * padding
        window_height = image_hight + 2 * padding

        # Size of application window
        self.window.geometry("{}x{}".format(window_width, window_height))
        # Don't allow resizing in the x or y direction
        self.window.resizable(False, False)

        self.topFrame.place(x=0, y=0, width=window_width, height=window_height)

        self.originalImageLabel.place(
            x=padding, y=padding, width=image_width, height=image_hight
        )
        self.processedImageLabel.place(
            x=(image_width + 2 * padding),
            y=padding,
            width=image_width,
            height=image_hight,
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
            y=(button_height + menu_height + 4 * padding),
            width=control_width,
            height=button_height,
        )
        self.greenJointLabel.place(
            x=(image_width * 2 + 3 * padding),
            y=(2 * button_height + menu_height + 5 * padding),
            width=control_width,
            height=label_height,
        )
        self.blueJointLabel.place(
            x=image_width * 2 + 3 * padding,
            y=(2 * button_height + menu_height + label_height + 6 * padding),
            width=control_width,
            height=label_height,
        )
        self.redJointLabel.place(
            x=image_width * 2 + 3 * padding,
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
            self.serialPort.set_name(self.serialPortName)
            self.serialPort.open()
        else:
            self.isStarted = False
            self.startButton.configure(text="Start processing")
            self.serialPort.close()

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

    def close_window(self):
        if self.isStarted:
            self.serialPort.close()
        self.window.destroy()


if __name__ == "__main__":
    # Create the GUI
    gui = RobotVision()
