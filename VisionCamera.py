#This module handles the camera and obtains the images for processing
from time import sleep
import cv2
import logging
from ImageProcessing import process_image
import pytesseract 
from PIL import Image
from difflib import SequenceMatcher
import enchant

class VisionCamera:
    def __init__(self, width, height) -> None:
        self.width = width
        self.height = height
        self.cam = cv2.VideoCapture(5)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        if not self.cam.isOpened():
            logging.error("Camera initialization failed.")
            raise Exception("Camera could not be opened")
        
    def similar(self, str1, str2):
        return SequenceMatcher(None, str1, str2).ratio()

    def record(self, frequency, motion_threshold=20000):
        """
        This function handles the picture sample. Frequency represents the number of
        smaples per second.
        """
        img_n = 0
        prev_frame = None
        pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
        try:
            while(True):
                ret, frame = self.cam.read()

                if not ret:
                    logging.warning("Failed to capture image!")
                    continue

                if True: #non_zero_count > motion_threshold:
                    img_n += 1

                    #Sending the image to processing
                    IMAGE = process_image(frame)
                    text = pytesseract.image_to_string(frame, config='--psm 6')
                    
                    print(text)
                    cv2.imshow("dsd", IMAGE)
                    

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    #text = pytesseract.image_to_string(IMAGE)
                    #print(text)

                else:
                    logging.info("No significant motion detected, skipping image.")

                sleep(1.0 / frequency)  # Adjust frequency of sampling

            
        except Exception as e:
            logging.error(f"An error occurred during recording: {e}")
        finally:
            self.cam.release()
            cv2.destroyAllWindows()
            logging.info("Camera resources released.")
