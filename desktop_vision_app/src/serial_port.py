# Communication with serial port
import serial

# Multi-threading
import threading


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
