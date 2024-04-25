"""This module is used as a gateway to the OSC api."""
import asyncio
import concurrent.futures
import json
import logging
import os.path
import shutil
from typing import Tuple, Optional, List

import psutil
import requests
from colorama import Fore
from tqdm import tqdm

import osc_api_config
from osc_api_config import OSCAPISubDomain
from osc_api_models import OSCSequence, OSCPhoto, OSCUser
from storage import Storage

LOGGER = logging.getLogger('osc_tools.osc_api_gateway')


def _upload_url(env: OSCAPISubDomain, resource: str) -> str:
    return _osc_url(env) + '/' + _version() + '/' + resource + '/'


def _osc_url(env: OSCAPISubDomain) -> str:
    base_url = __protocol() + env.value + __domain()
    return base_url


def __protocol() -> str:
    return osc_api_config.PROTOCOL


def __domain() -> str:
    return osc_api_config.DOMAIN


def _version() -> str:
    return osc_api_config.VERSION


def _website(url: str) -> str:
    return url.replace("-api", "").replace("api.", "")


class OSCAPIResource:

    @classmethod
    def base_url(cls, env: OSCAPISubDomain):
        return _osc_url(env)

    @classmethod
    def video(cls, env: OSCAPISubDomain, video_id=None) -> str:
        if video_id is None:
            return _osc_url(env) + "/" + "2.0/video/"
        return _osc_url(env) + "/" + "2.0/video/" + str(video_id)

    @classmethod
    def photo_part(cls, env: OSCAPISubDomain) -> str:
        return _osc_url(env) + "/" + "2.0/photo-part/"

    @classmethod
    def photo(cls, env: OSCAPISubDomain, photo_id=None) -> str:
        if photo_id is None:
            return _osc_url(env) + "/" + "2.0/photo/"
        return _osc_url(env) + "/" + "2.0/photo/" + str(photo_id)

    @classmethod
    def sequence(cls, env: OSCAPISubDomain, sequence_id=None) -> str:
        if sequence_id is None:
            return _osc_url(env) + "/2.0/sequence/"
        return _osc_url(env) + "/2.0/sequence/" + str(sequence_id)

    @classmethod
    def sequence_details(cls, env: OSCAPISubDomain, sequence_id=None) -> str:
        return _osc_url(env) + "/details/" + str(sequence_id)

    @classmethod
    def user(cls, env: OSCAPISubDomain, user_name=None) -> str:
        if user_name is None:
            return _osc_url(env) + "/" + "2.0/user/"
        return _osc_url(env) + "/" + "2.0/user/" + str(user_name)


class OSCApiMethods:
    """This is a factory class that creates API methods based on environment"""

    @classmethod
    def sequence_create(cls, env: OSCAPISubDomain) -> str:
        """this method will return the link to sequence create method"""
        return _osc_url(env) + "/" + _version() + "/sequence/"

    @classmethod
    def sequence_details(cls, env: OSCAPISubDomain) -> str:
        """this method will return the link to the sequence details method"""
        return _osc_url(env) + "/details"

    @classmethod
    def user_sequences(cls, env: OSCAPISubDomain) -> str:
        """this method returns the urls to the list of sequences that
        belong to a user"""
        return _osc_url(env) + "/my-list"

    @classmethod
    def resource(cls, env: OSCAPISubDomain, resource_name: str) -> str:
        """this method returns the url to a resource"""
        return _osc_url(env) + '/' + resource_name

    @classmethod
    def photo_list(cls, env: OSCAPISubDomain) -> str:
        """this method returns photo list URL"""
        return _osc_url(env) + '/' + _version() + '/sequence/photo-list/'

    # @classmethod
    # def login(cls, env: OSCAPISubDomain, provider: str) -> Optional[str]:
    #     """this method returns login URL"""
    #     if provider == "google":
    #         return _osc_url(env) + '/auth/google/client_auth'
    #     if provider == "facebook":
    #         return _osc_url(env) + '/auth/facebook/client_auth'
    #     # default to OSM
    #     return _osc_url(env) + '/auth/openstreetmap/client_auth'


class OSCApi:
    """This class is a gateway for the API"""

    def __init__(self, env: OSCAPISubDomain):
        self.environment = env

    def calculate_disk_space(self, total_items, path):
        def _get_free_space_gb(path):
            disk_usage = psutil.disk_usage(path)
            free_space_gb = disk_usage.free / (2 ** 30)
            return free_space_gb

        result = (total_items * 1.5 / 1024)
        print(
            f"{Fore.LIGHTGREEN_EX}Approximately {Fore.LIGHTYELLOW_EX}{result.real:.2f} GB {Fore.LIGHTGREEN_EX}space to be used{Fore.RESET}.\n"
            f"{Fore.LIGHTGREEN_EX}Your disk has {Fore.LIGHTYELLOW_EX}{_get_free_space_gb(path):.2f} GB{Fore.RESET}{Fore.LIGHTGREEN_EX} of free space, do you want to continue?")
        choice = input(f"{Fore.LIGHTBLUE_EX}Do you want to continue? (yes/no): ").lower()
        if choice == 'yes' or choice == 'y':
            print(f"{Fore.LIGHTGREEN_EX}Ongoing...")
        elif choice == 'no' or choice == 'n':
            print(f"{Fore.LIGHTRED_EX}Operation canceled.")
            exit()
        else:
            print("Invalid choice!")
            self.calculate_disk_space(total_items, path)

    def _sequence_page(self, user_name, page, pbar) -> Tuple[List[OSCSequence], Exception]:
        try:
            parameters = {'ipp': 500,
                          'page': page,
                          'username': user_name}
            login_url = OSCApiMethods.user_sequences(self.environment)
            response = requests.post(url=login_url, data=parameters)
            json_response = response.json()

            sequences = []
            if 'currentPageItems' in json_response:
                items = json_response['currentPageItems']
                for item in items:
                    sequence = OSCSequence.sequence_from_json(item)
                    sequences.append(sequence)
            else:
                LOGGER.debug("No sequences found for user: %s", user_name)

            # Update the progress bar once per page
            pbar.update(1)

            return sequences, json_response, None
        except requests.RequestException as ex:
            return None, ex

    # def authorized_user(self, provider: str, token: str, secret: str) -> Tuple[OSCUser, Exception]:
    #     """This method will get a authorization token for OSC API"""
    #     try:
    #         data_access = {'request_token': token,
    #                        'secret_token': secret
    #                        }
    #         login_url = OSCApiMethods.login(self.environment, provider)
    #         response = requests.post(url=login_url, data=data_access)
    #         json_response = response.json()
    #
    #         if 'osv' in json_response:
    #             osc_data = json_response['osv']
    #             user = OSCUser()
    #             missing_field = None
    #             if 'access_token' in osc_data:
    #                 user.access_token = osc_data['access_token']
    #             else:
    #                 missing_field = "access token"
    #
    #             if 'id' in osc_data:
    #                 user.user_id = osc_data['id']
    #             else:
    #                 missing_field = "id"
    #
    #             if 'username' in osc_data:
    #                 user.name = osc_data['username']
    #             else:
    #                 missing_field = "username"
    #
    #             if 'full_name' in osc_data:
    #                 user.full_name = osc_data['full_name']
    #             else:
    #                 missing_field = "fullname"
    #
    #             if missing_field is not None:
    #                 return None, Exception("OSC API bug. OSCUser missing " + missing_field)
    #
    #         else:
    #             return None, Exception("OSC API bug. OSCUser missing username")
    #
    #     except requests.RequestException as ex:
    #         return None, ex
    #
    #     return user, None

    def get_photos(self, sequence_id, page=None) -> Tuple[List[OSCPhoto], Optional[Exception]]:
        try:
            photo_url = OSCAPIResource.photo(self.environment)
            has_more_data = True
            photos = []
            current_page = page
            if page is None or page < 1:
                current_page = 1
            while has_more_data:
                response = requests.get(photo_url,
                                        params={"sequenceId": sequence_id,
                                                "page": current_page,
                                                "itemsPerPage": 500})
                json_response = response.json()
                result = json_response.get("result", {})
                photo_list = result.get("data", [])
                for photo_json in photo_list:
                    photo = OSCPhoto.photo_from_json(photo_json)
                    photos.append(photo)
                has_more_data = result.get("hasMoreData", False)
                if page is not None:
                    break
                if has_more_data:
                    current_page += 1
            return photos, None
        except requests.RequestException as ex:
            return [], ex

    def download_all_images(self, photo_list: [OSCPhoto],
                            track_path: str,
                            override=False,
                            workers: int = 10):
        """This method will download all images to a path overriding or not the files at
        that path. By default this method uses 10 parallel workers."""
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            loop = asyncio.new_event_loop()
            futures = [
                loop.run_in_executor(executor,
                                     self.get_image, photo, track_path, override)
                for photo in photo_list
            ]
            if not futures:
                loop.close()
                return

            loop.run_until_complete(asyncio.gather(*futures))
            loop.close()

    def get_image(self, photo: OSCPhoto, path: str, override=False) -> Optional[Exception]:
        """downloads the image at the path specified"""
        jpg_name = path + '/' + str(photo.sequence_index) + '.jpg'
        if not override and os.path.isfile(jpg_name):
            return None

        try:
            response = requests.get(OSCApiMethods.resource(self.environment,
                                                           photo.image_name),
                                    stream=True)
            if response.status_code == 200:
                with open(jpg_name, 'wb') as file:
                    response.raw.decode_content = True
                    shutil.copyfileobj(response.raw, file)
        except requests.RequestException as ex:
            return ex
        return None

    def user_sequences(self, user_name: str) -> Tuple[List[OSCSequence], Exception]:
        MERGED_RESPONSE = os.path.join(
            os.path.expanduser("~"),
            ".config",
            "mapilio",
            "configs",
            "MapSyncer",
            f"{user_name}_sequences_logs.json"
        )
        if not os.path.exists(MERGED_RESPONSE):
            sequences, error = self._user_sequences(user_name)
        else:
            sequences = []
            with open(MERGED_RESPONSE, 'r') as f:
                responses = json.load(f)
            for r in responses:
                response = responses[r]
                if 'currentPageItems' in response:
                    items = response['currentPageItems']
                    for item in items:
                        sequence = OSCSequence.sequence_from_json(item)
                        sequences.append(sequence)
            error = None
        return sequences, error

    def get_missing_sequences(self, user_name: str) -> Tuple[List[OSCSequence], Exception]:
        MERGED_RESPONSE = os.path.join(
            os.path.expanduser("~"),
            ".config",
            "mapilio",
            "configs",
            "MapSyncer",
            f"{user_name}_sequences_logs.json"
        )
        if os.path.exists(MERGED_RESPONSE):
            sequences, error = self._user_sequences(user_name)
        else:
            print("Json response not found")

        return sequences, error


    def _user_sequences(self, user_name: str) -> Tuple[List[OSCSequence], Exception]:
        """get all tracks for a user id """
        merged_json_response = {}
        print(
            f"Getting all sequences for user:{Fore.BLUE} {user_name}{Fore.RESET} from KartaView. It can take a while according to the number of sequences.")
        parameters = {'ipp': 500,
                      'page': 1,
                      'username': user_name}
        try:
            json_response = requests.post(url=OSCApiMethods.user_sequences(self.environment),
                                          data=parameters).json()
            merged_json_response.update({'0': json_response})

        except requests.RequestException as ex:
            return None, ex

        if 'totalFilteredItems' not in json_response:
            api_message = json_response.get('status', {}).get('apiMessage', 'Unknown Error')
            if api_message == "Invalid username!":
                return [], Exception("No Kartaview account associated with OpenStreetMap was found.")
            return [], Exception(f"OSC API error: {api_message}")

        total_items = int(json_response['totalFilteredItems'][0])
        pages_count = int(total_items / parameters['ipp']) + 1
        print(
            f"{Fore.BLUE}Total count of images: {Fore.LIGHTBLUE_EX}{total_items}{Fore.RESET}{Fore.BLUE} Total count of pages: {Fore.LIGHTBLUE_EX}{pages_count}")

        sequences = []
        if 'currentPageItems' in json_response:
            for item in json_response['currentPageItems']:
                sequences.append(OSCSequence.sequence_from_json(item))

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            loop = asyncio.new_event_loop()
            print(
                f"{Fore.LIGHTCYAN_EX}Fetching from Kartaview is a singular event. Future synchronizations will be completed more swiftly. Feel free to focus on other tasks while we handle this for you ☕️.{Fore.RESET}")
            pbar = tqdm(total=30, desc="Fetching sequences")  # Total is pages_count - 1 because range starts from 2
            futures = [
                loop.run_in_executor(executor,
                                     self._sequence_page, user_name, page, pbar)
                for page in range(2, 30)
            ]

            MERGED_RESPONSE = os.path.join(
                os.path.expanduser("~"),
                ".config",
                "mapilio",
                "configs",
                "MapSyncer",
                f"{user_name}_sequences_logs.json"
            )

            with open(MERGED_RESPONSE, "w") as file:
                json.dump(merged_json_response, file)

            if not futures:
                loop.close()
                return sequences, None

            done = loop.run_until_complete(asyncio.gather(*futures))
            pbar.close()
            loop.close()

            for idx, sequence_page_return in enumerate(done):
                # sequence_page method will return a tuple the first element
                # is a list of sequences

                merged_json_response.update({str(idx + 1): sequence_page_return[1]})

                sequences = sequences + sequence_page_return[0]
            with open(MERGED_RESPONSE, "w") as file:
                json.dump(merged_json_response, file)
            return sequences, None

    def sequence_link(self, sequence) -> str:
        """This method will return a link to OSC website page displaying the sequence
        sent as parameter"""
        sequence_details_url = OSCApiMethods.sequence_details(self.environment)
        return _website(f"{sequence_details_url}/{str(sequence.online_id)}")

    def download_metadata(self, sequence: OSCSequence, path: str, override=False):
        """this method will download a metadata file of a sequence to the specified path.
        If there is a metadata file at that path by default no override will be made."""
        if sequence.metadata_url is None:
            return None
        metadata_path = path + "/track.txt"
        if not override and os.path.isfile(metadata_path):
            return None

        try:
            response = requests.get(OSCApiMethods.resource(self.environment,
                                                           sequence.metadata_url),
                                    stream=True)
            if response.status_code == 200:
                with open(metadata_path, 'wb') as file:
                    response.raw.decode_content = True
                    shutil.copyfileobj(response.raw, file)
        except requests.RequestException as ex:
            return ex

        return None

    def get_sequence(self, sequence_id) -> Tuple[Optional[OSCSequence], Optional[Exception]]:
        try:
            sequence_url = OSCAPIResource.sequence(self.environment, sequence_id)
            response = requests.get(sequence_url)
            response.raise_for_status()
        except requests.RequestException as ex:
            return None, ex

        json_response = response.json()
        if json_response['status']['apiCode'] != 600:
            return None, Exception(json_response['status']['apiMessage'])

        result = json_response.get("result", {})
        sequence_json = result.get("data", {})
        sequence = OSCSequence.from_json(sequence_json)
        return sequence, None

    @staticmethod
    def download_resource(resource_url: str,
                          file_path: str,
                          storage: Storage,
                          override=False) -> Tuple[bool, Optional[Exception]]:
        if not override and storage.isfile(file_path):
            return True, None, None
        try:
            with requests.get(resource_url) as response:
                response.raise_for_status()
                storage.put(response.content, file_path + "partial")
                if os.path.exists(file_path + "partial"):
                    storage.rename(file_path + "partial", file_path)
            return True, None, None
        except requests.exceptions.RequestException as ex:
            if isinstance(ex, requests.exceptions.HTTPError) and ex.response.status_code == 404:
                modified_url = resource_url.replace("proc", "lth")
                try:
                    with requests.get(modified_url) as response:
                        response.raise_for_status()
                        storage.put(response.content, file_path + "partial")
                        storage.rename(file_path + "partial", file_path)

                    return True, None, file_path

                except requests.exceptions.RequestException as ex:
                    try:

                        storage.remove(file_path + "partial")
                    except Exception:
                        pass
                    print(f"Failed to download from modified URL {modified_url} to {file_path}: {ex}")
                    return False, ex, None
            else:
                try:
                    storage.remove(file_path + "partial")
                except Exception:
                    pass
                return False, ex, None
