import cv2
import numpy as np
from PIL import Image
import pytesseract

def process_image(image):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    equalized_image = clahe.apply(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
    binary_image = cv2.threshold(equalized_image, 127, 255, cv2.THRESH_BINARY)[1]

    return image

