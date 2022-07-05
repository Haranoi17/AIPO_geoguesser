from random import random
from imutils.object_detection import non_max_suppression
import numpy as np
import cv2
import sys
import pytesseract
from PIL import Image
import zipfile
import pathlib
import os
import time

# with zipfile.ZipFile('Tesseract-OCR.zip', 'r') as zip_ref:
    # zip_ref.extractall('.')
current_package_path = pathlib.Path(__file__).parent.resolve()

# pytesseract.pytesseract.tesseract_cmd =  r'.\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd =  os.path.join(current_package_path, 'Tesseract-OCR', 'tesseract.exe')


def getTextFromImage(image, net):
    # image = cv2.resize(image, None, fx=2, fy=2)

    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.GaussianBlur(image,(3,3),0)
    # ret,image = cv2.threshold(np.array(image), 125, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # cv2.imwrite("thresh{}.png".format(time.time()), image)
    config = '--oem 3 --psm 12'
    text = pytesseract.image_to_string(image, config=config)

    return text

def getTextFromPlate(image, net):
    image = cv2.resize(image, None, fx=2, fy=2)

    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.GaussianBlur(image,(3,3),0)
    # ret,image = cv2.threshold(np.array(image), 125, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # cv2.imwrite("thresh{}.png".format(time.time()), image)
    config = '--oem 3 --psm 6'
    text = pytesseract.image_to_string(image, config=config)

    return text

def getTextFromVideo(frame):
    # load the pre-trained EAST text detector
    print("[INFO] loading EAST text detector...")
    net = cv2.dnn.readNet('frozen_east_text_detection.pb')
    output = getTextFromImage(frame,net)   
    return output