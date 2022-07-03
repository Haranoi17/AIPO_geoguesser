import cv2
from nbformat import read
from car_plates_detection import car_plate_detection
from text_recognition import text_recognition
from language_detector import language_detection
import zipfile
import pathlib
import os

LANGUAGE = language_detection.LanguageIdentification()
current_package_path = pathlib.Path(__file__).parent.resolve()
zip_path = os.path.join(current_package_path, 'text_recognition', 'Tesseract-OCR.zip')
unzip_path = os.path.join(current_package_path, 'text_recognition')

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(unzip_path)

'''
    returns: {key, value}
    {'en': 0.18432828783988953, 'ROMANIA': 50.9, 'pt': 0.0625753104686737, 'UNITED KINGDOM': 100.0, 'vi': 0.16454465687274933, 'nn': 0.25713205337524414, 'es': 0.1808989942073822, 'eu': 0.03920429199934006, 'ro': 0.09386847168207169, 'lmo': 0.06671386957168579, 'gom': 0.09568020701408386, 'da': 0.04634846746921539, 'br': 0.05365986004471779, 'cy': 0.03737263381481171}
'''
def readVideo(filename):
    video = cv2.VideoCapture(filename)
    frame_width = int(video.get(3))
    frame_height = int(video.get(4))
    frame_size = (frame_width,frame_height)
    video.set(cv2.CAP_PROP_FPS, 1) 
    result = {}
    # load the pre-trained EAST text detector
    frame_counter = 0
    while(video.isOpened()):
        ret, frame = video.read()
        if ret == True:
            frame_counter += 1
            print("FRAME: {}".format(frame_counter))
           # call plate detection 
            plate_frame_arr, _ = car_plate_detection.detect_number(frame)
            for plate_frame in plate_frame_arr:
                # > call text detection on plate frame
                plate_frame_text = text_recognition.getTextFromPlate(plate_frame, None)
                plate_frame_text = plate_frame_text.replace("\n", " ")
                # remove characters that not letters or numbers
                plate_frame_text = list([val for val in plate_frame_text if val.isalnum() or val.isspace()])
                plate_frame_text = "".join(plate_frame_text)
                print("Plate text: ", plate_frame_text)
                # > call country detection
                if plate_frame_text:
                    plate_frame_text_country = car_plate_detection.get_countries_from_license_plate_code(plate_frame_text)
                    print("Plate country: ", plate_frame_text_country)
                    # save results with accuracy > 50
                    # avoid duplicates
                    for c in plate_frame_text_country:
                        if c[1] > 50 and c[0] not in result.keys():
                            result[c[0]] = c[1]
            # call text detection 
            # every 5th frame
            if frame_counter % 5 == 0:
                text_frame = text_recognition.getTextFromImage(frame, None)
                text_frame = text_frame.replace("\n", " ")
                # remove characters that not letters or numbers
                text_frame = list([val for val in text_frame if val.isalnum() or val.isspace()])
                text_frame = "".join(text_frame)
                # > call language detection
                print("Text: ", text_frame)
                text_frame_language = LANGUAGE.get_country(text_frame)
                print("Language detection: ", text_frame_language)
                if text_frame_language:
                    if text_frame_language[0] is not None:
                        if text_frame_language[0] not in result.keys():
                            result[text_frame_language[0]] = text_frame_language[2]
                    else:
                        if text_frame_language[1] not in result.keys():
                            result[text_frame_language[1]] = text_frame_language[2]
        else:
            break

    video.release()
    return result

def readImage(filename):
    img = cv2.imread(filename)
    result = {}
    # load the pre-trained EAST text detector
    if img is not None:
        # call plate detection 
        plate_frame_arr, _ = car_plate_detection.detect_number(img)
        for plate_frame in plate_frame_arr:
            # > call text detection on plate frame
            plate_frame_text = text_recognition.getTextFromPlate(plate_frame, None)
            plate_frame_text = plate_frame_text.replace("\n", " ")
            # remove characters that not letters or numbers
            plate_frame_text = list([val for val in plate_frame_text if val.isalnum() or val.isspace()])
            plate_frame_text = "".join(plate_frame_text)
            print("Plate text: ", plate_frame_text)
            # > call country detection
            if plate_frame_text:
                plate_frame_text_country = car_plate_detection.get_countries_from_license_plate_code(plate_frame_text)
                print("Plate country: ", plate_frame_text_country)
                # save results with accuracy > 50
                # avoid duplicates
                for c in plate_frame_text_country:
                    if c[1] > 50 and c[0] not in result.keys():
                        result[c[0]] = c[1]
        # call text detection 
        text_frame = text_recognition.getTextFromImage(img, None)
        text_frame = text_frame.replace("\n", " ")
        # remove characters that not letters or numbers
        text_frame = list([val for val in text_frame if val.isalnum() or val.isspace()])
        text_frame = "".join(text_frame)
        # > call language detection
        text_frame_language = LANGUAGE.get_country(text_frame)
        print("Language detection: ", text_frame_language)
        if text_frame_language:
            if text_frame_language[0] is not None:
                if text_frame_language[0] not in result.keys():
                    result[text_frame_language[0]] = text_frame_language[2]
            else:
                if text_frame_language[1] not in result.keys():
                    result[text_frame_language[1]] = text_frame_language[2]
    return result


# out = getTextFromVideo('2s.mp4')
# res = readVideo('dataset/car1.mp4')
# res = readImage('dataset/nd.png')
# res = readImage('dataset/car_plate.jpg')
res = readImage('dataset/simple.png')
# res = readVideo('dataset/2s.mp4')
print(res)
# res = readVideo('dataset/vid2.mov')