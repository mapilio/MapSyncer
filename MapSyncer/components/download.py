"""
This module is created in order to support the download of user uploaded data
"""

import logging
import os
import json
from concurrent.futures import (
    as_completed,
    ThreadPoolExecutor,
)
from typing import List, Tuple

from tqdm.auto import tqdm

from common_models import GPS
from storage import Local
from login_controller import LoginController
from osc_api_config import OSCAPISubDomain
from osc_api_gateway import OSCApi
from osc_api_models import OSCPhoto
from parsers.exif.exif import ExifParser
from get_exif import get_exif
from colorama import Fore, init

LOGGER = logging.getLogger('osc_tools.osc_utils')

def check_sequence_status(sequence_id):
    log_file = ".download_logs.json"
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            log_data_list = json.load(f)
            for entry in log_data_list:
                if entry["seq_id"] == sequence_id and entry["download_success"] and entry["upload_success"]:
                    return True
    return False


def select_sequences_to_download(sequences):
    print(f"{Fore.BLUE}Available sequences:")
    for index, sequence in enumerate(sequences):
        print(f"{index + 1}- ({sequence.online_id})")

    while True:
        try:
            selection = input(f"{Fore.LIGHTBLUE_EX}Enter the sequence numbers you want to download (comma-separated, a range such as 1-3, or 'all' for all sequences): {Fore.RESET}")
            if selection.lower() == "all":
                return sequences
            selected_sequences = parse_selection(selection, sequences)
            if selected_sequences:
                return selected_sequences
            else:
                print(f"{Fore.LIGHTRED_EX}Invalid selection. Please enter valid sequence numbers or 'all'.")
        except EOFError:
            print("Input interrupted. Please provide valid input.")


def parse_selection(selection, sequences):
    if selection.lower() == "all":
        return None

    selected_sequences = []
    parts = selection.replace(" ", "").split(",")
    for part in parts:
        if "-" in part:
            start, end = part.split("-")
            if start.isdigit() and end.isdigit():
                start_index = int(start)
                end_index = int(end)
                if 1 <= start_index <= end_index <= len(sequences):
                    selected_sequences.extend(sequences[start_index - 1:end_index])
                else:
                    return None
            else:
                return None
        elif part.isdigit():
            index = int(part)
            if 1 <= index <= len(sequences):
                selected_sequences.append(sequences[index - 1])
            else:
                return None
        else:
            return None
    return selected_sequences

def download_user_images(to_path):
    login_controller = LoginController(OSCAPISubDomain.PRODUCTION)
    # login to get the valid user
    user = login_controller.login()
    osc_api = login_controller.osc_api
    # get all the sequneces for this user
    sequences, error = osc_api.user_sequences(user.name,to_path)

    if error:
        print("Could not get sequences for the current user, try again or report a issue on "
                    "github")
        return

    selected_sequences = select_sequences_to_download(sequences)

    user_dir_path = os.path.join(to_path)
    os.makedirs(user_dir_path, exist_ok=True)

    # download each sequence
    for sequence in tqdm(selected_sequences, desc="Downloading sequences"):
        if sequence is None or isinstance(sequence, BaseException):
            continue

        sequence_path = os.path.join(user_dir_path, str(sequence.online_id))
        os.makedirs(sequence_path, exist_ok=True)
        if not check_sequence_status(sequence.online_id):
            download_success, _ , lth_images = _download_photo_sequence(osc_api,
                                                           sequence,
                                                           sequence_path,
                                                           add_gps_to_exif=True)


            if not download_success:
                LOGGER.info("There was an error downloading the sequence: %s", str(sequence.online_id))

            json_file_path = os.path.join(sequence_path, "mapilio_image_description.json")
            if not os.path.exists(json_file_path):
                get_exif(sequence.online_id, sequence_path, lth_images)
        else:
            print(f"{Fore.LIGHTYELLOW_EX}Sequence " + str(sequence.online_id) + " already uploaded to Mapilio")



def _download_photo_sequence(osc_api: OSCApi,
                             sequence,
                             sequence_path: str,
                             add_gps_to_exif: bool = False) -> Tuple[bool, List[OSCPhoto]]:
    photos, error = osc_api.get_photos(sequence.online_id)
    if error:
        return False, []
    # download metadata
    if sequence.metadata_url is not None:
        metadata_path = os.path.join(sequence_path, sequence.online_id + ".txt")
        osc_api.download_resource(sequence.metadata_url, metadata_path, Local())
        sequence.metadata_url = metadata_path

    # download photos
    download_success = True
    download_bar = tqdm(total=len(photos),
                        desc="Downloading sequence " + str(sequence.online_id))
    with ThreadPoolExecutor(max_workers=10) as executors:
        futures = [executors.submit(_download_photo,
                                    photo,
                                    sequence_path,
                                    osc_api,
                                    add_gps_to_exif) for photo in photos]
        lth_images = []
        for future in as_completed(futures):
            photo_success, _, filePath = future.result()
            if filePath is not None:
                lth_images.append(filePath)
            download_success = download_success and photo_success
            download_bar.update(1)
    log_file = ".download_logs.json"
    log_data = {
        "seq_id": sequence.online_id,
        "download_success": download_success,
        "upload_success": False
    }

    log_data_list = []
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            log_data_list = json.load(f)

    is_duplicate = any(entry["seq_id"] == sequence.online_id for entry in log_data_list)
    if not is_duplicate:
        log_data_list.append(log_data)

    with open(log_file, 'w') as f:
        json.dump(log_data_list, f, indent=4)

    if not download_success:
        LOGGER.info("Download failed for sequence %s", str(sequence.online_id))
        return False, [], []
    return True, photos , lth_images


def _download_photo(photo: OSCPhoto,
                    folder_path: str,
                    osc_api: OSCApi,
                    add_gps_to_exif: bool = False):
    photo_download_name = os.path.join(folder_path, str(photo._file_url.split("/")[-1].split(".")[0]) + ".jpg")
    local_storage = Local()
    photo_success, error , file_path = osc_api.download_resource(photo.photo_url(),
                                                     photo_download_name,
                                                     local_storage)


    if error or photo_success:
        LOGGER.debug("Failed to download image: %s", photo.photo_url())

    if add_gps_to_exif and photo_success:
        parser = ExifParser(photo_download_name, local_storage)
        if len(parser.items_with_class(GPS)) == 0:
            item = GPS()
            item.latitude = photo.latitude
            item.longitude = photo.longitude
            item.timestamp = photo.timestamp
            parser.add_items([item])
            parser.serialize()
    return photo_success, error , file_path