# run.py
import os
import shutil
import json
from mapilio_kit.components.login import list_all_users
from mapilio_kit.components.edit_config import edit_config
from mapilio_kit.base import authenticator
from .components.download import download_user_images,flask_app
import getpass
from colorama import (Fore,
                      init as init_colorama)
import requests
from .components.version_ import __version__

DOWNLOAD_LOGS = os.path.join(
        os.path.expanduser("~"),
        ".config",
        "mapilio",
        "configs",
        "MapSyncer",
        "download_logs.json"
    )

IMAGES_DOWNLOAD_PATH = os.path.join(
        os.path.expanduser("~"),
        ".cache",
        "mapilio",
        "MapSyncer",
        "images"
    )

def get_latest_version():
    url = "https://raw.githubusercontent.com/mapilio/MapSyncer/main/MapSyncer/components/version_.py"
    response = requests.get(url)
    if response.status_code == 200:
        content = response.text
        version_line = [line for line in content.split('\n') if '__version__' in line][0]
        latest_version = version_line.split('"')[1]
        return latest_version
    return None

def main():
    latest_version = get_latest_version()

    if latest_version:
        if latest_version > __version__:
            print(f"{Fore.RED}A newer version ({latest_version}) is available!")
            print(f'{Fore.RED}For latest MapSyncer version please update with "pip install mapsyncer --upgrade" \n')
        else:
            print(f"{Fore.GREEN}You have the latest MapSyncer version ({__version__}) installed.\n")
    else:
        print(f"{Fore.RED}Unable to fetch the latest MapSyncer version information.\n")

    init_colorama()

    print(f"{Fore.LIGHTCYAN_EX}To access the web interface of MapSyncer, simply navigate to the following URL:\n"
          f"http://localhost:5050/ in your web browser's address bar.\n{Fore.RESET}")

    if not os.path.exists(IMAGES_DOWNLOAD_PATH):
        os.makedirs(IMAGES_DOWNLOAD_PATH)

    flask_app(IMAGES_DOWNLOAD_PATH)


def get_args_mapilio(func):
    arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]
    return {arg: None for arg in arg_names}


def print_folder_structure(folder_path, indent=""):
    print(indent + os.path.basename(folder_path) + "/")
    subdirectories = [entry for entry in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, entry))]
    for i, subdirectory in enumerate(subdirectories):
        subdirectory_path = os.path.join(folder_path, subdirectory)
        if i == len(subdirectories):  print_folder_structure(subdirectory_path, indent + "    ")
        else:                         print_folder_structure(subdirectory_path, indent + "│-   ")


def check_auth():
    print("Please enter your mapilio account information to continue.\n"
          "If you don't have a mapilio account, please create one at https://mapilio.com/ \n")
    user_name = input("Enter your username: ").strip()
    user_email = input("Enter your email: ").strip()
    user_password = getpass.getpass("Enter mapilio user password: ").strip()

    if user_name and user_email and user_password:
        args = get_args_mapilio(edit_config)
        args["user_name"] = user_name
        args["user_email"] = user_email
        args["user_password"] = user_password
        check_authenticate = authenticator().perform_task(args)
        if check_authenticate:
            return check_authenticate
        else:
            check_auth()
    else:
        print("Please enter your username, email and password properly \n\n\n\n\n")
        check_auth()
def update_folder_status(folder_name_numeric, json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
        for folder in data:
            if folder.get('seq_id') == folder_name_numeric:
                uploaded_path = os.path.join(IMAGES_DOWNLOAD_PATH, folder.get('seq_id'))
                try:
                    shutil.rmtree(uploaded_path)
                except OSError as err:
                    print(f"Error: {uploaded_path} could not be deleted. - {err}")
                folder['upload_success'] = True
                break
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)

def folder_selection(path):
    print("Choose an option:")
    print("1. Upload all folders")
    print("2. Upload a specific folder")

    choice = input(f"{Fore.LIGHTGREEN_EX}Enter your choice (1 or 2): {Fore.RESET}")

    if choice == '1':
        print(f"{Fore.LIGHTYELLOW_EX}Uploading all folders...")
        folders_to_upload = []

        with open(DOWNLOAD_LOGS, 'r') as f:
            data = json.load(f)
            for folder in data:
                if not folder.get('json_success'):
                    print(f"{Fore.RED}The json file of the file with sequence id: {folder['seq_id']} was not found, please download the folder again.")
                    continue
                elif not folder.get('upload_success'):
                    folders_to_upload.append(folder.get('seq_id'))

        files = os.listdir(path)
        for file in files:
            file_path = os.path.join(path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

        for folder_name in os.listdir(path):
            folder_path = os.path.join(path, folder_name)
            if len(os.listdir(folder_path)) < 5:
                continue

            folder_name_numeric = ''.join(filter(str.isdigit, folder_name))

            if folder_name_numeric in folders_to_upload:
                upload_command = f"mapilio_kit upload --processed {folder_path}"
                result = os.system(upload_command)

                if result != 0:
                    print(f"{Fore.RED}Error occurred while uploading {folder_path}")
                    continue

            update_folder_status(folder_name_numeric, DOWNLOAD_LOGS)
        print(f"{Fore.LIGHTGREEN_EX}All folders uploaded. 🎉")

    elif choice == '2':
        print(f"{Fore.BLUE}Available folders: {Fore.RESET}")
        print_folder_structure(path)

        folder_name = input("Enter the specific folder name: ")
        folder_name_numeric = ''.join(filter(str.isdigit, folder_name))
        print(f"{Fore.YELLOW}Uploading folder '{folder_name_numeric}'... {Fore.RESET}")

        upload_command = f"mapilio_kit upload --processed {path + '/' + folder_name_numeric}"
        with open(DOWNLOAD_LOGS, 'r') as f:
            data = json.load(f)
            for folder in data:
                if folder.get('seq_id') == folder_name_numeric:
                    if folder.get('upload_success') == True:
                        print(f"{Fore.LIGHTGREEN_EX}Folder '{folder_name_numeric}' was already uploaded 🎉.{Fore.RESET}")
                        folder_selection(path)
                    elif folder.get('json_success') == False:
                        print(f"{Fore.RED}The json file of the file with sequence id: {folder['seq_id']} was not found, please download the folder again.")
                        folder_selection(path)
        result = os.system(upload_command)

        if result != 0:
            print(f"{Fore.RED}Error occurred while uploading {folder_name_numeric}")
        else:
            update_folder_status(folder_name_numeric, DOWNLOAD_LOGS)

        folder_selection(path)

    else:
        print(f"{Fore.RED}Invalid choice. Please enter 1 or 2.{Fore.RESET}")
        folder_selection(path)

if __name__ == "__main__":
    main()
