#This module handles the camera and obtains the images for processing
from time import sleep
from cv2 import *
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