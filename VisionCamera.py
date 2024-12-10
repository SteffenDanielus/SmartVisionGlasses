#This module handles the camera and obtains the images for processing
from time import sleep
from cv2 import imshow
from cv2 import VideoCapture
from cv2 import imwrite
import cv2
class VisionCamera:
    def __init__(self, width, height) -> None:
        self.width = width
        self.height = height

    def record(self, frequency):
        """
        This function handles the picture sample. Frequency represents the number of
        smaples per second.
        """
        while(True):
            print("Takeing samples...")
            print("Sleeping for: " + str(1.0/frequency))
            sleep(1.0/frequency)
            cam = VideoCapture(0)
            result, image = cam.read()
            if result:
                imshow("sd", image)
                imwrite("testimage.png", image, [cv2.IMWRITE_JPEG_QUALITY, 90])
                cv2.destroyAllWindows()
                break