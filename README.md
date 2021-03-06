# OpenCV Vision for an Underactuated Robot Manipulator

This repository contains all the source code related to the computer-vision part of an academic research project for controlling an underactuated robot manipulator done in years 2016 and 2017. The control algorithm of the robot is not provided is this repository.

![Our underactuated robot manipulator](images/underactuated-robot-manipulator.jpg)

This application is written in Python using [Tkinter](https://docs.python.org/3/library/tkinter.html) and [OpenCV](https://opencv.org/).

This is a demo of the application running in Linux:

![](images/new-program-demo.gif)

This application and its GUI can run in all desktop OSes with no extra work needed. This is a screenshot of it running in Windows 10:

![](images/new-program-windows.png)

## Old Versions

The v1, v2, and v3 versions of this project were written in Visual Studio using C# and [EmguCV](https://www.emgu.com/) and were hosted locally on my PC. I decided to put them in a GitHub repository in order to share it with other developers.

## Current Development

Due to some limitations of C# and .NET for cross-platform application design and difficulties in using [OpenCV](https://opencv.org/) I refactored the code and translated it into Python and used [Tkinter](https://docs.python.org/3/library/tkinter.html) for GUI design.


## Install dependencies

Python Version: 3.8.10

```console
pip install -r "./desktop_vision_app/requirements.txt"
```

## Tutorials

### Tkinter

- [Hello World in Tkinter](https://www.geeksforgeeks.org/hello-world-in-tkinter/)
- [Change the Tkinter Label Text](https://www.delftstack.com/howto/python-tkinter/how-to-change-the-tkinter-label-text/)
- [Tkinter Place](https://www.pythontutorial.net/tkinter/tkinter-place/)

### OpenCV + Tkinter

- [How display multi videos with threading using tkinter in python?](https://stackoverflow.com/questions/65876044/how-display-multi-videos-with-threading-using-tkinter-in-python)
- [Supercharge Your Classes With Python super()](https://realpython.com/python-super/)
- [Refresh Tkinter Widgets using after()](https://www.geeksforgeeks.org/python-after-method-in-tkinter/)

### OpenCV

- [Difference between HSV and HSV_FULL in opencv?](https://stackoverflow.com/questions/21782420/difference-between-hsv-and-hsv-full-in-opencv)
- [How to detect two different colors using `cv2.inRange` in Python-OpenCV?](https://stackoverflow.com/questions/48109650/how-to-detect-two-different-colors-using-cv2-inrange-in-python-opencv)
- [Performing Bitwise Operations on Images using OpenCV](https://medium.com/featurepreneur/performing-bitwise-operations-on-images-using-opencv-6fd5c3cd72a7)
- [Morphological Transformations](https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html)
- [How to Detect Contours in Images using OpenCV in Python](https://www.thepythoncode.com/article/contour-detection-opencv-python)
- [Python OpenCV ??? Find center of contour](https://www.geeksforgeeks.org/python-opencv-find-center-of-contour/)
- [Drawing shapes](https://opencv-tutorial.readthedocs.io/en/latest/draw/draw.html)
- [Cropping an Image using OpenCV](https://learnopencv.com/cropping-an-image-using-opencv/)

### Misc

- [What is the Python equivalent of static variables inside a function?](https://stackoverflow.com/questions/279561/what-is-the-python-equivalent-of-static-variables-inside-a-function)
- [Digital Low Pass Filter Code Generator](http://www.schwietering.com/jayduino/filtuino/)