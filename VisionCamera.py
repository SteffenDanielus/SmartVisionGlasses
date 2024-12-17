#This module handles the camera and obtains the images for processing
from time import sleep
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
            cam = cv2.VideoCapture(0)
            cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            result, image = cam.read()
            if result:
                cv2.imshow("sd", image)
                cv2.imwrite("testimage.jpeg", image, [cv2.IMWRITE_JPEG_QUALITY, 90])
                cv2.destroyAllWindows()
                break