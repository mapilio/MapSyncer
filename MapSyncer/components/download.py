"""
This module is created in order to support the download of user uploaded data
"""

import logging
import os
import json
import platform
import subprocess
from concurrent.futures import (
    as_completed,
    ThreadPoolExecutor,
)
from typing import List, Tuple

from tqdm.auto import tqdm

from common_models import GPS
from storage import Local
from osc_api_config import OSCAPISubDomain
from osc_api_gateway import OSCApi
from osc_api_models import OSCPhoto
from parsers.exif.exif import ExifParser
from get_exif import get_exif
from colorama import Fore
progress = {}

LOGGER = logging.getLogger('osc_tools.osc_utils')

DOWNLOAD_LOGS = os.path.join(
        os.path.expanduser("~"),
        ".config",
        "mapilio",
        "configs",
        "MapSyncer",
        "download_logs.json"
    )

def check_sequence_status(sequence_id):
    if os.path.exists(DOWNLOAD_LOGS):
        if os.path.getsize(DOWNLOAD_LOGS) == 0:
            return False
        with open(DOWNLOAD_LOGS, 'r') as f:
            log_data_list = json.load(f)
            for entry in log_data_list:
                if entry.get("seq_id") == sequence_id and entry.get("download_success") and entry.get("upload_success"):
                    return True
    return False


def select_sequences_to_download(sequences):
    print(f"{Fore.BLUE}Available sequences:")
    for index, sequence in enumerate(sequences):
        print(f"{index + 1}- ({sequence.online_id})")

    while True:
        try:
            selection = input(
                f"{Fore.LIGHTBLUE_EX}Enter the sequence numbers you want to download (comma-separated, a range such as 1-3, or 'all' for all sequences): {Fore.RESET}")
            if selection.lower() == "all":
                return sequences
            selected_sequences = parse_selection(selection, sequences)
            if selected_sequences:
                return selected_sequences
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

# def flask_app(folder_path):
#     #TODO: Flask will be up by app.app, shouldnt use subprocesser
#     login_controller = LoginController(OSCAPISubDomain.PRODUCTION)
#     user = login_controller.login()
#     flaskPath = os.path.join('/'.join(os.path.dirname(os.path.abspath(__file__)).split("/")[:-1]), "app.py")
#     command = f"python3 {flaskPath} --username {user.name} --to_path {folder_path}"
#     if platform.system() == "Windows":
#         command = f"python {flaskPath} --username {user.name} --to_path {folder_path} "
#         subprocess.Popen(['cmd', '/c', 'start', 'cmd', '/k', command])
#     elif platform.system() == "Linux":
#         try:
#             subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f"{command}; read -p 'Press Enter to exit'"])
#         except:
#             subprocess.Popen(['bash', '-c', f"{command}; read -p 'Press Enter to exit'"])
#     elif platform.system() == "Darwin":  # macOS
#         def get_virtualenv_path():
#             try:
#                 venv_path = subprocess.check_output(['which', 'python']).decode().strip()
#                 if 'usr' not in venv_path:
#                     return venv_path.split('bin')[0]
#             except subprocess.CalledProcessError:
#                 pass
#                 return None
#
#         venv_path = get_virtualenv_path()
#         if venv_path:
#             venv_activate_command = f'source {venv_path}/bin/activate && '
#         else:
#             venv_activate_command = ''
#
#         applescript = f'tell application "Terminal" to do script "{venv_activate_command}python3 {flaskPath} --username {user.name} --to_path {folder_path}"'
#         subprocess.run(['osascript', '-e', applescript])
#     else:
#         print("Unsupported operating system")


def download_user_images(to_path,user_name,selected_sequences_id=None):
    # login_controller = LoginController(OSCAPISubDomain.PRODUCTION)
    # login to get the valid user
    # user = login_controller.login()
    # osc_api = login_controller.osc_api
    osc_api = OSCApi(OSCAPISubDomain.PRODUCTION)
    # get all the sequneces for this user
    sequences, error = osc_api.user_sequences(user_name)

    if error:
        print("Could not get sequences for the current user, try again or report a issue on "
              "github")
        return
    if selected_sequences_id is None:
        selected_sequences = select_sequences_to_download(sequences)
    else:
        selected_sequences = [sequence for sequence in sequences if sequence.online_id == selected_sequences_id]
    # create the user directory

    user_dir_path = os.path.join(to_path)
    os.makedirs(user_dir_path, exist_ok=True)

    # download each sequence
    for sequence in tqdm(selected_sequences, desc="Downloading sequences"):
        if sequence is None or isinstance(sequence, BaseException):
            continue

        sequence_path = os.path.join(user_dir_path, str(sequence.online_id))
        os.makedirs(sequence_path, exist_ok=True)
        if not check_sequence_status(sequence.online_id):
            download_success, photos, lth_images = _download_photo_sequence(osc_api,
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
            current_item_index = download_bar.n
            progress[sequence.online_id] = current_item_index


    log_data = {
        "seq_id": sequence.online_id,
        "download_success": download_success,
        "upload_success": False,
        "json_success": False
    }

    log_data_list = []
    if os.path.exists(DOWNLOAD_LOGS):
        with open(DOWNLOAD_LOGS, 'r') as f:
            log_data_list = json.load(f)

    for entry in log_data_list:
        if entry["seq_id"] == sequence.online_id:
            entry["download_success"] = download_success
            break
    else:
        log_data_list.append(log_data)

    with open(DOWNLOAD_LOGS, 'w') as f:
        json.dump(log_data_list, f, indent=4)

    if not download_success:
        LOGGER.info("Download failed for sequence %s", str(sequence.online_id))
        return False, [], []
    return True, photos, lth_images


def _download_photo(photo: OSCPhoto,
                    folder_path: str,
                    osc_api: OSCApi,
                    add_gps_to_exif: bool = False):
    photo_download_name = os.path.join(folder_path, str(photo._file_url.split("/")[-1].split(".")[0]) + ".jpg")
    local_storage = Local()
    photo_success, error, file_path = osc_api.download_resource(photo.photo_url(),
                                                                photo_download_name,
                                                                local_storage)

    if error or photo_success:
        LOGGER.debug("Failed to download image: %s", photo.photo_url())

    if add_gps_to_exif and photo_success:
        try:
            parser = ExifParser(photo_download_name, local_storage)
        except FileNotFoundError:
            print("File not found: " + photo_download_name)
        if len(parser.items_with_class(GPS)) == 0:
            item = GPS()
            item.latitude = photo.latitude
            item.longitude = photo.longitude
            item.timestamp = photo.timestamp
            parser.add_items([item])
            parser.serialize()
    return photo_success, error, file_path
