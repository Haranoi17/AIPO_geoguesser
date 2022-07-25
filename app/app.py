import cv2
from nbformat import read
from car_plates_detection import car_plate_detection
from text_recognition import text_recognition
from language_detector import language_detection
import zipfile
import pathlib
import os
import numpy as np
import utils
from constants import *
from tqdm import tqdm
from typing import Dict, Tuple, List

LANGUAGE = language_detection.LanguageIdentification()

current_package_path = pathlib.Path(__file__).parent.resolve()
zip_path = os.path.join(current_package_path, 'text_recognition', 'Tesseract-OCR.zip')
unzip_path = os.path.join(current_package_path, 'text_recognition')


with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(unzip_path)


def analyse_frame(frame, language_results, plate_code_results):
    
    # call plate detection 
    plate_frame_arr, _ = car_plate_detection.detect_number(frame)
    for plate_frame in plate_frame_arr:
        # > call text detection on plate frame
        plate_frame_text = text_recognition.getTextFromPlate(plate_frame, None)
        plate_frame_text = plate_frame_text.replace("\n", " ")
        # remove characters that not letters or numbers
        plate_frame_text = list([val for val in plate_frame_text if val.isalnum() or val.isspace()])
        plate_frame_text = "".join(plate_frame_text)
        # print("Plate text: ", plate_frame_text)

        # > call country detection
        if plate_frame_text and car_plate_detection.is_license_plate_code_valid(plate_frame_text):
            countries_from_license_plate_code = car_plate_detection.get_countries_from_license_plate_code(plate_frame_text)
            for country, country_label, accuracy in countries_from_license_plate_code:
                if accuracy > PLATE_CODE_ACCURACY_THRESHOLD:
                    try:
                        plate_code_results[country_label].append(accuracy) 
                    except KeyError:
                        plate_code_results[country_label] = [accuracy, ]

    # > call text detection 
    text_frame = text_recognition.getTextFromImage(frame, None)
    text_frame = text_frame.replace("\n", " ")
    text_frame = [word+" " if len(word) >= MIN_WORD_LENGTH else "" for word in text_frame.split(" ")]
    text_frame = "".join(text_frame)
    # remove characters that not letters or numbers
    text_frame = list([val for val in text_frame if val.isalnum() or val.isspace()])
    text_frame = "".join(text_frame)

    # > call language detection
    if text_frame:
        # print("Text: ", text_frame)
        country, country_label, accuracy = LANGUAGE.get_country(text_frame)
        if accuracy > LANGUAGE_ACCURACY_THRESHOLD:
            try:
                language_results[country_label].append(accuracy) 
            except KeyError:
                language_results[country_label] = [accuracy, ]
        # print("Language detection: ", text_frame_language)

    return language_results, plate_code_results


def process_video(filename) -> Tuple[Dict, Dict]:
    
    language_results = {}
    plate_code_results = {}
    video_frames = utils.load_video(
        filename, 
        every_n_frame=EVERY_N_FRAME
    )
    if not video_frames:
        raise Exception("Video frames list is empty")
    for frame in tqdm(video_frames):
        language_results, plate_code_results = analyse_frame(
            frame, 
            language_results, 
            plate_code_results
        )

    keys_to_drop = []
    for key in language_results.keys():
        if len(language_results[key]) < MINIMAL_NUMBER_OF_LANGUAGE_ENTRIES:
            keys_to_drop.append(key)
    for key in keys_to_drop:
        del language_results[key]

    for key in language_results.keys():
        n = len(language_results[key])
        if key == 'en':
            n *= WEAKEN_ENGLISH_CONTANT
        language_results[key] = n * np.mean(language_results[key])

    for key in plate_code_results.keys():
        n = len(plate_code_results[key])
        plate_code_results[key] = n * np.mean(plate_code_results[key])
    return language_results, plate_code_results

def process_image(filename) -> Tuple[Dict, Dict]:
    
    language_results = {}
    plate_code_results = {}
    image = cv2.imread(filename)
    # if not image:
    #     raise Exception("Image is empty")
    language_results, plate_code_results = analyse_frame(
        image, 
        language_results, 
        plate_code_results
    )
    return language_results, plate_code_results


def make_prediction(language_results:Dict, plate_code_results:Dict):
    partial_results = utils.merge_dictionaries(language_results, plate_code_results)
    summed_values = sum([value for _, value in partial_results.items()])
    partial_results = sorted(partial_results.items(), key=lambda x: x[1], reverse=True)
    results = []
    for key, value in partial_results:
        results.append(
            (
                car_plate_detection.get_full_name_from_country_label(key), 
                value/summed_values*100
            )
        )
    return results


def run_module(filename: str) -> List[Tuple[str, float]]:
    # filename = 'dataset/Rotterdam.mp4'
    if filename.endswith("mp4"):
        process_function = process_video
    else:
        process_function = process_image

    results = make_prediction(*process_function(filename))

    print(f"{results = }")
    return results


if __name__ == '__main__':
    run_module('dataset/Rotterdam.mp4')
