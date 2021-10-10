# GUI design
import tkinter as tk

# for Image and ImageTk types
from PIL import Image, ImageTk

# Communication with serial port
from serial.tools import list_ports

# Image Processing Operations Management
from image_processing import *


class RobotVisionGUI:
    # GUI main class
    def __init__(
        self,
        window,
        windowTitle,
        iconPath,
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
        self.window.title(windowTitle)
        # Icon of application window
        self.window.iconphoto(False, tk.PhotoImage(file=iconPath))

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
