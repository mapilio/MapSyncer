import os.path
import random
import requests
import json
import string
from colorama import Fore, Style, init
import version_
from calculation.distance import Distance
import imagesize


def check_seq(prev_lon, prev_lat, curr_lon, curr_lat, next_lon, next_lat, threshold=50):
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
    dist1 = Distance.haversine(lon1=prev_lon, lat1=prev_lat, lon2=curr_lon, lat2=curr_lat)
    dist2 = Distance.haversine(lon1=curr_lon, lat1=curr_lat, lon2=next_lon, lat2=next_lat)
    if dist1 > threshold and dist2 <= threshold:
        return True
    elif dist1 < threshold:
        return False
    elif dist1 > threshold and dist2 > threshold:
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


# def get_api_access_token():
#     """
#     This function retrieves the OpenStreetCam API access token from the credentials.json file.
#     """
#     CREDENTIALS_FILE = os.path.join(
#         os.path.expanduser("~"),
#         ".config",
#         "mapilio",
#         "configs",
#         "MapSyncer",
#         "credentials.json"
#     )
#
#     try:
#         with open(CREDENTIALS_FILE, 'r') as credentials_file:
#             credentials = json.load(credentials_file)
#             osm_token = credentials.get("osm", {}).get("token")
#             return osm_token
#     except FileNotFoundError:
#         print(f"Error: {CREDENTIALS_FILE} not found.")
#         return None
#     except json.JSONDecodeError as e:
#         print(f"Error decoding JSON in {CREDENTIALS_FILE}: {e}")
#         return None


def get_exif(seq_id, sequence_path, lth_images):
    """
    This function gets the exif data from the OpenStreetCam API and saves it to a JSON file.

    Args:
        seq_id (str): The sequence ID.
        sequence_path (str): The path to the sequence folder.
    """
    DOWNLOAD_LOGS = os.path.join(
        os.path.expanduser("~"),
        ".config",
        "mapilio",
        "configs",
        "MapSyncer",
        "download_logs.json"
    )

    # access_token = get_api_access_token()

    # if access_token is None:
    #     print("Access token not found. Please check your credentials.")
    #     return sequence_path

    url_details = f"https://api.openstreetcam.org/details"
    params = {
        'id': seq_id
    }
    mapilio_description = []
    page_count = 1
    try:
        hasMoreData = True
        processed_count = 0

        response_details = requests.post(url_details, data=params)
        api_data_details = response_details.json()

        while hasMoreData:
            # No need to use access token.
            # url = f"https://api.openstreetcam.org/2.0/photo/?access_token={access_token}&sequenceId={seq_id}&page={page_count}"
            url = f"https://api.openstreetcam.org/2.0/photo/?&sequenceId={seq_id}&page={page_count}"
            response_photos = requests.get(url)
            api_data_photos = response_photos.json()

            if response_details.status_code != 200 or response_photos.status_code != 200:
                print(
                    f"\n{Fore.RED}Operation of sequence id: '{seq_id}' was skipped due to a '{response_details.status_code}' status code error.{Fore.RESET}")
                json_file = ".download_logs.json"
                with open(json_file, 'r') as f:
                    data = json.load(f)
                for item in data:
                    if item.get('seq_id') == seq_id:
                        item['json_success'] = False
                with open(json_file, 'w') as f:
                    json.dump(data, f)
                return sequence_path

            if 'result' in api_data_photos and 'data' in api_data_photos['result']:

                vfov = 0
                fov = 0
                fLen = 0

                for idx, api_photo_data in enumerate(api_data_photos['result']['data']):
                    curr_lat = float(api_photo_data["matchLat"]) if api_photo_data.get(
                        "matchLat") is not None else float(api_photo_data["lat"])
                    curr_lon = float(api_photo_data["matchLng"]) if api_photo_data.get(
                        "matchLng") is not None else float(api_photo_data["lng"])
                    if idx + 2 < len(api_data_photos['result'][
                                         'data']) and idx > 1:  # cannot use idx + 1 ,idx >0 in this condition. in this situation the last and first items that should not stand alone in sequence.
                        prev_lat = float(api_data_photos['result']['data'][idx - 1]["matchLat"]) if \
                            api_data_photos['result']['data'][idx - 1].get("matchLat") is not None else float(
                            api_data_photos['result']['data'][idx - 1]["lat"])
                        next_lat = float(api_data_photos['result']['data'][idx + 1]["matchLat"]) if \
                            api_data_photos['result']['data'][idx + 1].get("matchLat") is not None else float(
                            api_data_photos['result']['data'][idx + 1]["lat"])
                        prev_lon = float(api_data_photos['result']['data'][idx - 1]["matchLng"]) if \
                            api_data_photos['result']['data'][idx - 1].get("matchLng") is not None else float(
                            api_data_photos['result']['data'][idx - 1]["lng"])
                        next_lon = float(api_data_photos['result']['data'][idx + 1]["matchLng"]) if \
                            api_data_photos['result']['data'][idx + 1].get("matchLng") is not None else float(
                            api_data_photos['result']['data'][idx + 1]["lng"])
                        situation = check_seq(prev_lon, prev_lat, curr_lon, curr_lat, next_lon, next_lat)
                    else:
                        situation = False
                    if idx % 250 == 0 or situation:
                        current_unique_id = unique_sequence_id_generator(letter_count=8, digit_count=4)

                    absolute_path = os.path.abspath(f'{sequence_path}/{api_photo_data["name"]}')
                    if absolute_path in lth_images:
                        width, height = imagesize.get(absolute_path)
                        api_photo_data["width"] = str(width)
                        api_photo_data["height"] = str(height)

                    if api_data_details["osv"]["cameraParameters"] is not None:
                        vfov = api_data_details["osv"]["cameraParameters"]["vFoV"]
                        fov = api_data_details["osv"]["cameraParameters"]["hFoV"]
                        fLen = api_data_details["osv"]["cameraParameters"]["fLen"]

                    device_name = api_data_details.get("osv", {}).get("deviceName", "")
                    platform = api_data_details.get("osv", {}).get("platform")

                    if platform == "iOS" or "iPhone" in platform:
                        device_make, device_model = "Apple", device_name.split(",")[0].replace("iPhone", "iPhone ")

                    elif platform == "Android" and " " in device_name:
                        device_make, device_model = device_name.split(" ")[0], device_name.split(" ", 1)[1]

                    elif platform == "samsung":
                        device_make, device_model = "Samsung", device_name

                    elif platform == "GoPro":
                        device_make, device_model = "GoPro", device_name

                    else:
                        device_make, device_model = "Unknown", "Unknown"

                    photo_data = \
                        {
                            "latitude": float(api_photo_data["matchLat"]) if api_photo_data.get(
                                "matchLat") is not None else float(api_photo_data["lat"]),
                            "longitude": float(api_photo_data["matchLng"]) if api_photo_data.get(
                                "matchLng") is not None else float(api_photo_data["lng"]),
                            "captureTime": api_photo_data["shotDate"],
                            "altitude": 0,
                            "sequenceUuid": current_unique_id,
                            "source": f"KartaView-v{version_.__version__}",
                            "sourceUser": api_data_details.get("osv", {}).get("user"),
                            "heading": float(api_photo_data["heading"]) if api_photo_data.get(
                                "heading") is not None else 0,
                            "orientation": 1,
                            "roll": 0,
                            "pitch": 0,
                            "yaw": 0,
                            "carSpeed": 0,
                            "deviceMake": device_make,
                            "deviceModel": device_model,
                            "imageSize": api_photo_data["width"] + "x" + api_photo_data["height"],
                            "fov": fov,
                            "megapixels": 0,
                            "vfov": vfov,
                            "focalLength": fLen,
                            "filename": api_photo_data["name"],
                            "path": ""
                        }

                    if api_photo_data.get("gpsAccuracy") is not None: photo_data["accuracy_level"] = float(api_photo_data["gpsAccuracy"])
                    mapilio_description.append(photo_data)
                    processed_count += 1
                page_count += 1
                hasMoreData = api_data_photos['result'].get('hasMoreData', False)
            else:
                if "empty" in api_data_photos['status']['apiMessage']:
                    print(f"{Fore.YELLOW}{api_data_photos['status']['apiMessage']}, so skipping the {page_count} page.{Fore.RESET}")
                    hasMoreData = False


        description_information = {
            "Information": {
                "total_images": processed_count,
                "processed_images": processed_count,
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

        with open(DOWNLOAD_LOGS, 'r') as f:
            data = json.load(f)
        for item in data:
            if item.get('seq_id') == seq_id:
                item['json_success'] = True
        with open(DOWNLOAD_LOGS, 'w') as f:
            json.dump(data, f)

    except requests.exceptions.RequestException as e:
        print(f"Error making the request: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

    return sequence_path
