# run.py
import os
import sys

from mapilio_kit.components.login import list_all_users
from mapilio_kit.components.edit_config import edit_config
from mapilio_kit.base import authenticator
from .components.download import download_user_images
import getpass
from colorama import Fore, init


def main():
    init()
    folder_path = input(f"{Fore.YELLOW}Please enter the path to the folder to download images to:\n{Fore.RESET}")
    folder_path = folder_path.strip('\'"')

    if 'mapilio_images' in folder_path:
        download_user_images(folder_path)
    else:
        folder_path = os.path.join(folder_path, 'mapilio_images')

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        download_user_images(folder_path)

    check_authenticate = False

    if len(list_all_users()) == 0:
        check_authenticate = check_auth()
    elif len(list_all_users()) >= 2:
        username = input("Found multiple Mapilio accounts. Please specify your username.\n")
    else:
        check_authenticate = True

    if check_authenticate:

        if folder_path is not None and len(os.listdir(folder_path)) == 0:
            print(f"{Fore.RED}Something went wrong. Please check your destination path.{Fore.RESET}")
            exit()

        folder_selection(folder_path)


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


def folder_selection(path):
    print("Choose an option:")
    print("1. Upload all folders")
    print("2. Upload a specific folder")

    choice = input(f"{Fore.LIGHTGREEN_EX}Enter your choice (1 or 2): ")

    if choice == '1':
        print("Uploading all folders...")
        upload_commands = []
        for folder_name in os.listdir(path):
            folder_path = os.path.join(path, folder_name)
            if len(os.listdir(folder_path)) < 5: continue
            upload_command = f"mapilio_kit upload --processed {folder_path}"
            upload_commands.append(upload_command)

        for command in upload_commands:
            os.system(command)

    elif choice == '2':

        print(f"{Fore.BLUE}Available folders: {Fore.RESET}")
        print_folder_structure(path)

        folder_name = input("Enter the specific folder name: ")
        folder_name_numeric = ''.join(filter(str.isdigit, folder_name))
        print(f"{Fore.YELLOW}Uploading folder '{folder_name_numeric}'... {Fore.RESET}")

        upload_command = f"mapilio_kit upload --processed {path + '/' + folder_name_numeric}"
        os.system(upload_command)

    else:
        print(f"{Fore.RED}Invalid choice. Please enter 1 or 2.{Fore.RESET}")
        folder_selection(path)


if __name__ == "__main__":
    main()
