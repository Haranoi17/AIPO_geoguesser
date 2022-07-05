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


def is_license_plate_code_valid(license_plate_code:str) -> bool:
    """Function validating license plate code. It should contain at least one digit.

    Arguments:
        license_plate_code {str} -- code from license plate
    
    Returns:
        results {bool} -- True if code contains at least one digit 
    """
    return any(char.isdigit() for char in license_plate_code)

def get_countries_from_license_plate_code(license_plate_code:str) -> List[Tuple[str, str, float]]:
    """Function reading text from car plate and returning list of tuples of
    country, country label (code) and probability. 
    The latter means the probability license plate code
    is from that country. Function uses data scrapping from a spanish page
    dedicated for this problem.

    Arguments:
        license_plate_code {str} -- code from license plate
    
    Returns:
        results {List[Tuple[str, str, float]]} -- list of pairs containing country,
            country label (code) and corresponding probability
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
                country, country_label = country.rsplit(' ', 1)
                country_label = country_label.replace('(', '').replace(')', '')
                country_label = convert_country_label(country_label)
                percentage = tr.find('span', class_="progress-completed").getText()
                percentage = float(percentage.replace('%', ''))
                results.append((country, country_label, percentage/100.0))
                # print(f"[INFO] country: {country}, country_label: {country_label}, percentage: {percentage:.2f}")

    except HTTPError as he:
        print(he, url)
    except ValueError as ve:
        print("Conversion Error:", ve)
    except Exception as e:
        print(e)
        raise e
    
    return results


def convert_country_label(country_label:str) -> str:
    """Function converting vehicle's country code to ISO2 country code.

    Arguments:
        country_label {str} -- country code in "vehicle standard"
    
    Returns:
        code {str} -- ISO2 country code
    """
    url = "https://country-code.cl/"
    ISO2_COLUMN = 3 # fourth td in row
    VEHICLE_COLUMN = 8 # nineth td in row
    try:
        country_label = country_label.lower()
        page = urlopen(url)
        page = BeautifulSoup(page, 'html.parser')
        content = page.find(id="countriesTable")
        if not content:
            raise Exception("Countries table not found. It may have been changed")
        for tr in content.tbody.findAll('tr'):
            tds = tr.findAll('td')
            if country_label == tds[VEHICLE_COLUMN].getText().lower():
                code = tds[ISO2_COLUMN].find('a').string.lower()
                return code.replace(u'\xa0', '')
    except HTTPError as he:
        print(he, url)
    except Exception as e:
        print(e)
        # raise e
    return None


def get_full_name_from_country_label(country_label:str) -> str:
    """Function converting ISO2 country code to its full name.

    Arguments:
        country_label {str} -- ISO2 country code
    
    Returns:
        name {str} -- country full name (or country_label if not found)
    """
    url = "https://country-code.cl/"
    FULL_NAME_COLUMN = 2 # third td in row
    ISO2_COLUMN = 3 # fourth td in row
    try:
        country_label = country_label.lower()
        page = urlopen(url)
        page = BeautifulSoup(page, 'html.parser')
        content = page.find(id="countriesTable")
        if not content:
            raise Exception("Countries table not found. It may have been changed")
        for tr in content.tbody.findAll('tr'):
            tds = tr.findAll('td')
            if country_label == tds[ISO2_COLUMN].find('a').string.lower() \
            .replace(u'\xa0', ''):
                name = tds[FULL_NAME_COLUMN].get('title')
                return name
    except HTTPError as he:
        print(he, url)
    except Exception as e:
        print(e)
        # raise e
    return country_label


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