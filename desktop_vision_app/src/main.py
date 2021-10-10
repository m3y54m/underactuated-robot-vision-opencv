# GUI design
import tkinter as tk

# Path of files
import pathlib

# GUI for this application
from robot_vision_gui import RobotVisionGUI

SRC_PATH = pathlib.Path(__file__).parent.resolve()
ICON_PATH = SRC_PATH.parent.resolve().joinpath("assets/icon.png")
VDO_PATH = str(SRC_PATH.parent.resolve().joinpath("assets/sample_video.mp4"))


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
        "Robot Vision Application",
        ICON_PATH,
        videoSource,
        videoFrameRate,
        desiredAspectRatio,
        serialPortBaud,
        guiUpdateInterval,
    )
