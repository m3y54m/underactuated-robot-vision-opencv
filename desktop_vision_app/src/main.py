# GUI design
import tkinter as tk

# Communication with serial port
import serial
from serial.tools import list_ports

import time

class RobotVision():
    def __init__(self):

        self.portNamesList = []
        self.isAnyPortAvailable = False
        self.get_available_serial_ports()
        
        self.window = tk.Tk()
        # Title of application window
        self.window.title("Robot Vision Application")
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
        self.startButton.pack()

        self.label = tk.Label(self.frame2, text="Blank")
        self.label.pack()

        # Blocking loop for GUI (Always put at the end)
        self.window.mainloop()

    def start_button_command(self):
        self.label.configure(text=self.selectedPort.get())

    def scan_button_command(self):
        self.get_available_serial_ports()
        self.update_option_menu()

    def get_available_serial_ports(self):

        # Clear portNames list
        self.portNamesList = []
        # Get a list of available serial ports
        portsList = list_ports.comports()
        # Sort based on port names
        portsList = sorted(portsList)

        for port in portsList:
            self.portNamesList.append(port.device)

        if len(self.portNamesList) == 0:
            self.isAnyPortAvailable = False
        else:
            self.isAnyPortAvailable = True

    def update_option_menu(self):

        if self.isAnyPortAvailable:
            self.portsOptionMenu.configure(state="normal")
        else:
            self.portNamesList = ["No ports available"]
            self.portsOptionMenu.configure(state="disabled")

        # Remove old items
        self.portsOptionMenu["menu"].delete(0, "end")
        # Add new items
        for portName in self.portNamesList:
            self.portsOptionMenu["menu"].add_command(
                label=portName, command=tk._setit(self.selectedPort, portName)
            )
        # Set default value of selectedPort
        self.selectedPort.set(self.portNamesList[0])


if __name__ == "__main__":
    # Create the GUI
    gui = RobotVision()
    

