import tkinter as tk


class RobotVisionUI():
    def __init__(self):
        self.root = tk.Tk()
        # Title of application window
        self.root.title("Robot Vision Application")
        # Size of application window
        self.root.geometry("500x500")
        # Don't allow resizing in the x or y direction
        self.root.resizable(False, False)

        self.frame = tk.Frame(self.root, padx=10, pady=10)
        self.frame.pack()

        self.label = tk.Label(self.frame, text="Blank")
        self.label.pack()

        self.button = tk.Button(
            self.frame, text="Say Hello!", command=self.button_command)
        self.button.pack()

        self.portsList = ["One", "Two", "Three"]
        self.selectedPort = tk.StringVar(self.root)
        self.selectedPort.set(self.portsList[0])
        self.portsOptionMenu = tk.OptionMenu(
            self.frame, self.selectedPort, *self.portsList,command=self.option_menu_command)
        self.portsOptionMenu.config(width=100)
        self.portsOptionMenu.pack()

        self.root.mainloop()

    def button_command(self):
        self.label.configure(text="Hello Wolrd!")

    def option_menu_command(self, value):
        self.label.configure(text=value)

    def scan_available_serial_ports(self):
        pass


if __name__ == "__main__":
    ui = RobotVisionUI()
