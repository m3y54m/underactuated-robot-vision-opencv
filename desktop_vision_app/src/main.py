# GUI design
import tkinter as tk

# Communication with serial port
import serial
from serial.tools import list_ports


class RobotVisionUI(object):
    def __init__(self):

        self.portNamesList = ["No ports available"]
        self.isAnyPortAvailable = False

        self.root = tk.Tk()
        # Title of application window
        self.root.title("Robot Vision Application")
        # Size of application window
        self.root.geometry("500x500")
        # Don't allow resizing in the x or y direction
        self.root.resizable(False, False)

        self.frame1 = tk.Frame(self.root, bg="white", padx=10, pady=10)
        self.frame1.pack()

        self.scanButton = tk.Button(
            self.frame1,
            text="Scan serial ports",
            command=self.scan_available_serial_ports,
        )
        self.scanButton.pack()

        self.selectedPort = tk.StringVar(self.root)
        # Set default value of selectedPort
        self.selectedPort.set(self.portNamesList[0])
        self.portsOptionMenu = tk.OptionMenu(
            self.frame1, self.selectedPort, *self.portNamesList
        )
        self.portsOptionMenu.configure(state="disabled")
        self.portsOptionMenu.pack()

        self.frame2 = tk.Frame(self.root, bg="yellow", padx=10, pady=10)
        self.frame2.pack()

        self.startButton = tk.Button(
            self.frame2,
            text="Start processing",
            command=self.start_image_processing,
        )
        self.startButton.pack()

        self.label = tk.Label(self.frame2, text="Blank")
        self.label.pack()

        self.root.mainloop()

    def start_image_processing(self):
        self.label.configure(text=self.selectedPort.get())

    def option_menu_command(self, value):
        self.label.configure(text=value)

    def scan_available_serial_ports(self):
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

        # Update OptionMenu
        self.update_option_menu()

    def update_option_menu(self):

        if self.isAnyPortAvailable:
            self.portsOptionMenu.configure(state="active")
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
    ui = RobotVisionUI()
