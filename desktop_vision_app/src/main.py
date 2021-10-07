# GUI design
import tkinter as tk

# Communication with serial port
import serial
from serial.tools import list_ports

# Multi-threading
import threading

# Path of files
import pathlib

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
        # Size of application window
        self.window.geometry("500x500")
        # Don't allow resizing in the x or y direction
        self.window.resizable(False, False)

        self.mainFrame = tk.Frame(self.window, bg="blue", padx=10, pady=10)
        self.mainFrame.pack()

        self.frame1 = tk.Frame(self.mainFrame, bg="white", padx=10, pady=10)
        self.frame1.pack()

        self.scanButton = tk.Button(
            self.frame1,
            text="Scan serial ports",
            command=self.scan_button_command,
        )
        self.scanButton.pack()

        self.selectedPort = tk.StringVar(self.mainFrame)
        # Set default value of selectedPort
        if self.isAnyPortAvailable == False:
            self.portNamesList = ["No ports available"]
        self.selectedPort.set(self.portNamesList[0])

        self.portsOptionMenu = tk.OptionMenu(
            self.frame1, self.selectedPort, *self.portNamesList
        )

        if self.isAnyPortAvailable == False:
            self.portsOptionMenu.configure(state="disabled")

        self.portsOptionMenu.pack()

        self.frame2 = tk.Frame(self.mainFrame, bg="yellow", padx=10, pady=10)
        self.frame2.pack()

        self.startButton = tk.Button(
            self.frame2,
            text="Start processing",
            command=self.start_button_command,
        )
        if self.isAnyPortAvailable == False:
            self.startButton.configure(state="disabled")
        self.startButton.pack()

        self.greenJointLabel = tk.Label(self.frame2, text="Green join position")
        self.greenJointLabel.pack()

        self.blueJointLabel = tk.Label(self.frame2, text="Blue joint position")
        self.blueJointLabel.pack()

        self.redJointLabel = tk.Label(self.frame2, text="Red joint position")
        self.redJointLabel.pack()

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


if __name__ == "__main__":
    # Create the GUI
    gui = RobotVision()
