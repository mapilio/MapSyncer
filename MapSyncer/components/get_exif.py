import os.path
import random
import requests
import json
import cv2
import string
from colorama import Fore, Style, init
from calculation.distance import Distance



def check_seq(prev_lon,prev_lat,curr_lon,curr_lat,next_lon,next_lat,threshold=50):
    """
                                                            next_coord
                                                                    *
        prev_coord
                *

                                curr_coord
                                        *
        it calculate distance between curr coordinate with previous and next coordinate. and make a decision to whether change the sequence or not.
    Args:
        prev_lon:
        prev_lat:
        curr_lon:
        curr_lat:
        next_lon:
        next_lat:

    Returns:
        situation
    """
    dist1=Distance.haversine(lon1=prev_lon, lat1=prev_lat, lon2=curr_lon, lat2=curr_lat)
    dist2=Distance.haversine(lon1=curr_lon,lat1=curr_lat,lon2=next_lon,lat2=next_lat)
    if dist1>threshold and dist2<=threshold:
        return True
    elif dist1<threshold:
        return False
    elif dist1>threshold and dist2>threshold:
        print(f"{Fore.YELLOW} The current point is far away from other points.{Fore.RESET}")
        return False


def unique_sequence_id_generator(letter_count: int = 8, digit_count: int = 4) -> str:
    """
    :param letter_count: Count of random letter
    :param digit_count: Count of random number
    :return: Unique sequence name
    """

    str1 = ''.join((random.choice(string.ascii_letters) for x in range(letter_count))) + '-'
    str1 += ''.join((random.choice(string.digits) for x in range(digit_count))) + '-'
    str1 += ''.join((random.choice(string.digits) for x in range(digit_count))) + '-'
    str1 += ''.join((random.choice(string.digits) for x in range(digit_count))) + '-'
    str1 += ''.join((random.choice(string.ascii_letters) for x in range(letter_count)))
    sam_list = list(str1)
    final_string = ''.join(sam_list)
    return final_string

def get_api_access_token():
    """
    This function retrieves the OpenStreetCam API access token from the credentials.json file.
    """
    credentials_file_path = 'credentials.json'

    try:
        with open(credentials_file_path, 'r') as credentials_file:
            credentials = json.load(credentials_file)
            osm_token = credentials.get("osm", {}).get("token")
            return osm_token
    except FileNotFoundError:
        print(f"Error: {credentials_file_path} not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in {credentials_file_path}: {e}")
        return None

def get_exif(seq_id, sequence_path, lth_images):
    """
    This function gets the exif data from the OpenStreetCam API and saves it to a JSON file.

    Args:
        seq_id (str): The sequence ID.
        sequence_path (str): The path to the sequence folder.
    """
    access_token = get_api_access_token()

    if access_token is None:
        print("Access token not found. Please check your credentials.")
        return sequence_path

    url = f"https://api.openstreetcam.org/2.0/photo/?access_token={access_token}&sequenceId={seq_id}"

    try:
        response = requests.get(url)
        response.raise_for_status()

        api_data = response.json()

        if 'result' in api_data and 'data' in api_data['result']:
            mapilio_description = []

            vfov = 0
            fov = 0

            for idx,api_photo_data in enumerate(api_data['result']['data']):
                curr_lat=float(api_photo_data["matchLat"]) if api_photo_data.get("matchLat") is not None else float(api_photo_data["lat"])
                curr_lon=float(api_photo_data["matchLng"]) if api_photo_data.get("matchLng") is not None else float(api_photo_data["lng"])
                if idx + 2 < len(api_data['result']['data']) and idx > 1: # cannot use idx + 1 ,idx >0 in this condition. in this situation the last and first items that should not stand alone in sequence.
                    prev_lat=float(api_data['result']['data'][idx-1]["matchLat"]) if api_data['result']['data'][idx-1].get("matchLat") is not None else float(api_data['result']['data'][idx-1]["lat"])
                    next_lat=float(api_data['result']['data'][idx+1]["matchLat"]) if api_data['result']['data'][idx+1].get("matchLat") is not None else float(api_data['result']['data'][idx+1]["lat"])
                    prev_lon=float(api_data['result']['data'][idx-1]["matchLng"]) if api_data['result']['data'][idx-1].get("matchLng") is not None else float(api_data['result']['data'][idx-1]["lng"])
                    next_lon=float(api_data['result']['data'][idx+1]["matchLng"]) if api_data['result']['data'][idx+1].get("matchLng") is not None else float(api_data['result']['data'][idx+1]["lng"])
                    situation=check_seq(prev_lon,prev_lat,curr_lon,curr_lat,next_lon,next_lat)
                else: situation=False
                if idx % 250 == 0 or situation:
                    current_unique_id = unique_sequence_id_generator(letter_count=8, digit_count=4)

                if api_photo_data.get("cameraParameters") is not None:
                    vfov = api_photo_data["cameraParameters"].get("vFoV")
                    fov = api_photo_data["cameraParameters"].get("hFoV")
                absolute_path = os.path.abspath(f'{sequence_path}/{api_photo_data["name"]}')
                if absolute_path in lth_images:
                    img = cv2.imread(absolute_path)
                    api_photo_data["width"]=str(img.shape[1])
                    api_photo_data["height"]=str(img.shape[0])

                photo_data = \
                {
                    "latitude": float(api_photo_data["matchLat"]) if api_photo_data.get("matchLat") is not None else float(api_photo_data["lat"]),
                    "longitude": float(api_photo_data["matchLng"]) if api_photo_data.get("matchLng") is not None else float(api_photo_data["lng"]),
                    "captureTime": api_photo_data["shotDate"],
                    "altitude": 0,
                    "sequenceUuid": current_unique_id,
                    "source": "KartaView",
                    "heading": float(api_photo_data["heading"]) if api_photo_data.get("heading") is not None else 0,
                    "orientation": 1,
                    "roll": 0,
                    "pitch": 0,
                    "yaw": 0,
                    "carSpeed": 0,
                    "deviceMake": "none",
                    "deviceModel": "none",
                    "imageSize": api_photo_data["width"] + "x" + api_photo_data["height"],
                    "fov": fov,
                    "megapixels": 0,
                    "vfov": vfov,
                    "filename": api_photo_data["name"],
                    "accuracy_level": float(api_photo_data["gpsAccuracy"]),
                    "path": ""
                }

                mapilio_description.append(photo_data)
            processed = len(mapilio_description)
            description_information = {
                "Information": {
                    "total_images": processed,
                    "processed_images": processed,
                    "failed_images": 0,
                    "duplicated_images": 0,
                    "id": "8323ff0a01fe49d1b55e610279f62828",
                    "device_type": "Desktop"
                }
            }
            mapilio_description.append(description_information)
            save_path = os.path.join(sequence_path, 'mapilio_image_description.json')
            with open(save_path, 'w') as outfile:
                json.dump(mapilio_description, outfile)
        else:
            print("No 'data' key found in the JSON response.")

    except requests.exceptions.RequestException as e:
        print(f"Error making the request: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

    return sequence_path
