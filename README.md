# OpenCV Vision for an Underactuated Robot Manipulator

This repository contains all the source code related to the computer-vision part of a academic research project for controlling an underactuated robot manipulator in years 2016 and 2017. The control algorithm of the robot is not provided is this repository.

![Our underactuated robot manipulator](images/underactuated-robot-manipulator.jpg)

The v1, v2, and v3 versions of this project were written in Visual Studio using C# and [EmguCV](https://www.emgu.com/) and were hosted locally on my PC. I decided to put them in a GitHub repository in order to share it with other developers.

This is a screenshot of the UI of old vision-based control app in Windows, written in Visual Studio.

![](images/old-program-ui.png)

And this is the another screenshot with image processing results:

![](images/old-program-screenshot-working.jpg)

Due to some limitations of C# and .NET for cross-platform application design and difficulties in using [OpenCV](https://opencv.org/) library I refactored the code and translated it to Python and used [Tkinter](https://docs.python.org/3/library/tkinter.html) for GUI design.

Further development of this project will add this feature(s):

- Write [OpenCV](https://opencv.org/) image processing code in Python

## Tutorials

### Tkinter

- [Hello World in Tkinter](https://www.geeksforgeeks.org/hello-world-in-tkinter/)
- [Change the Tkinter Label Text](https://www.delftstack.com/howto/python-tkinter/how-to-change-the-tkinter-label-text/)
- [Tkinter Place](https://www.pythontutorial.net/tkinter/tkinter-place/)