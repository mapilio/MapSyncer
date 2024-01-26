import os.path
import random
import requests
import json
import cv2
import string


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
                if idx % 250 == 0:
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
