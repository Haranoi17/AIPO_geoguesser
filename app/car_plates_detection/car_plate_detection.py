from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.error import HTTPError
from typing import List, Tuple
import cv2
import os
import pathlib

BASE_URL = "https://www.ofesauto.es/en/know-the-nationality-of-a-vehicle-through-its-plate-number/?matricula="

current_package_path = pathlib.Path(__file__).parent.resolve()
        # os.path.join(current_package_path, 'lang_model', 'lid.176.bin')
LIC_DATA = cv2.CascadeClassifier(os.path.join(current_package_path, 'haarcascade_russian_plate_number.xml'))


def get_countries_from_license_plate_code(license_plate_code:str) -> List[Tuple[str, float]]:
    """Function reading text from car plate and returning list of tuples of
    country and probability. The latter means the probability license plate code
    is from that country. Function uses data scrapping from a spanish page
    dedicated for this problem.

    Arguments:
        license_plate_code {str} -- code from license plate
    
    Returns:
        results {List[Tuple[str, float]]} -- list of pairs containing country and
            corresponding probability
    """

    # replacing spaces with pluses (need for url)
    url = BASE_URL + license_plate_code.replace(' ', '+')

    results = []

    try:
        page = urlopen(url)
        page = BeautifulSoup(page, 'html.parser')
        content = page.findAll('div', {"class": "col-xs-12 table-responsive"})
        if content:
            for tr in content[0].tbody.findAll('tr'):
                country = tr.find('div', class_="cell-zona").getText()
                # splitting country from code by last occurence of space (rsplit)
                country, code = country.rsplit(' ', 1)
                code = code.replace('(', '').replace(')', '')
                percentage = tr.find('span', class_="progress-completed").getText()
                percentage = float(percentage.replace('%', ''))
                results.append((country, percentage))
                # print(f"[INFO] country: {country}, code: {code}, percentage: {percentage:.2f}")

    except HTTPError as he:
        print(he, url)
    except ValueError as ve:
        print("Conversion Error:", ve)
    except Exception as e:
        print(e)
        raise e
    
    return results


def detect_number(img):
    """Function using Cascade classifier to detect car plates in image. 
    Returns cropped image with detected plates.
    
    Arguments:
        img -- image we want to detect car plates in

    Returns:
        cropped_img -- cropped image with detected, if not detected it returns None
    """ 

    temp = img.copy()
    detected_plates_rectangle = LIC_DATA.detectMultiScale(img, 1.2)
    cropped_img = []
    for rectangle in detected_plates_rectangle:
        (x, y, w, h) = rectangle
        cv2.rectangle(temp, (x, y), (x+w, y+h), (0, 255, 0), 3)
        cropped_img.append(img[y:y+h, x:x+w])
    return cropped_img, temp