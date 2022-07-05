import cv2
from typing import List, Dict

def load_video(filename:str, every_n_frame:int = 1) -> List:
    """Function loading video from filename.

    Arguments:
        filename {str} -- path or filename to the video
        every_n_frame -- loads every n-th frame of the video (default set to 1)

    Returns:
        video_frames -- list of frames from the video
    """
    video = cv2.VideoCapture(filename)
    frame_width = int(video.get(3))
    frame_height = int(video.get(4))
    frame_size = (frame_width,frame_height)
    video.set(cv2.CAP_PROP_FPS, 1) 
    video_frames = []
    i = 0
    while(video.isOpened()):
        ret, frame = video.read()
        if ret and ((i % every_n_frame) == 0):
            video_frames.append(frame)
        else:
            if not ret:
                break
        i += 1
    video.release()
    return video_frames



def merge_dictionaries(dict_1:Dict, dict_2:Dict) -> Dict:
    """Custom function for merging two result dictionaries.
    Values under the same key are added.
    """
    merged_dict = {}
    try:
        merged_dict = {**dict_1, **dict_2}
        for key, value in merged_dict.items():
            if key in dict_1 and key in dict_2:
                    merged_dict[key] += dict_1[key]
    except Exception as e:
        print(e)

    return merged_dict