import cv2 as cv
import math
import numpy as np

import pathlib

SRC_PATH = pathlib.Path(__file__).parent.resolve()
IMG_PATH = str(SRC_PATH.parent.resolve().joinpath("assets/sample_frame2.jpg"))

inputImage = cv.imread(IMG_PATH)


def crop_image(inputImage, desiredAspectRatio):

    imageHeight = inputImage.shape[0]
    imageWidth = inputImage.shape[1]
    currentAspectRatio = imageWidth / imageHeight

    if currentAspectRatio > desiredAspectRatio:

        desiredWidth = int(imageHeight * desiredAspectRatio)
        diff = int((imageWidth - desiredWidth) / 2)
        croppedImage = inputImage[:, int(diff) : int(imageWidth - diff)]

    elif currentAspectRatio < desiredAspectRatio:

        desiredHeight = int(imageWidth / desiredAspectRatio)
        diff = int((imageHeight - desiredHeight) / 2)
        croppedImage = inputImage[int(diff) : int(imageHeight - diff), :]

    else:
        croppedImage = inputImage

    return croppedImage


cv.imwrite("temp.jpg", crop_image(inputImage, 1.33))
