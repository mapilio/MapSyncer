import json
import math
import os
import shutil
import ssl
import webbrowser

import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from mapilio_kit.base import authenticator
from mapilio_kit.components.utilities.edit_config import edit_config
from mapilio_kit.components.auth.login import list_all_users
from mapilio_kit.base.loader import upload
from osm_login_python.core import Auth

from MapSyncer.components.download import download_user_images, check_sequence_status, progress
from MapSyncer.components.osc_api_gateway import OSCAPISubDomain
from MapSyncer.components.osc_api_gateway import OSCApi
from MapSyncer.components.ssl import ssl_create
from MapSyncer.config import DOWNLOAD_LOGS, IMAGES_PATH, CERT_PEM, KEY_PEM, MAPILIO_API_ENDPOINT, MAPILIO_CONFIG_PATH, \
    client_id, \
    client_secret

ssl_create()
app = Flask(__name__)
app.secret_key = "nnp6kt5DEheyZha8ez2WUSzJ"


def get_args_mapilio(func):
    arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]
    return {arg: None for arg in arg_names}


def save_data(data):
    try:
        with open(DOWNLOAD_LOGS, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(e)
        return None


def load_data():
    try:
        with open(DOWNLOAD_LOGS, encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(e)
        return None


def remove_mapilio_account():
    if os.path.exists(MAPILIO_CONFIG_PATH):
        os.remove(MAPILIO_CONFIG_PATH)
        return True
    return False


osm_auth = Auth(
    osm_url="https://www.openstreetmap.org",
    client_id="_W2iScgbQwmvYggNsSjhXMFuWzMRLBssxLMZMrxMktU",
    client_secret="rx-qjH487o480w-h-8c0nSvUlXf_Jwx-KnywDlrh3KY",
    secret_key="nnp6kt5DEheyZha8ez2WUSzJ",
    login_redirect_uri="https://127.0.0.1:5050/authenticate/",
    scope="read_prefs"
)


def check_kartaview_authenticate():
    if session.get('user_name') or request.form.get('user_name'):
        return True
    return False


@app.route('/', methods=['GET'])
def login():
    karta_auth = check_kartaview_authenticate()
    if karta_auth:
        return redirect(url_for('display_sequence'))
    else:
        return redirect('/kartaview-login')


@app.route('/kartaview-login', methods=['GET'])
def kartaview_login_page():
    return render_template('kartaview-login.html')


# OpenStreetMap-Kartaview Login
@app.route('/authenticate-kartaview', methods=['POST'])
def authenticate_kartaview():
    login_url = osm_auth.login()
    parsed_data = json.loads(json.dumps(login_url))
    url = parsed_data['login_url']
    return redirect(url)


@app.route('/authenticate/', methods=['GET'])
def callback():
    global osm_token_to_mapilio
    access_token = osm_auth.callback(request.url)
    osm_token_to_mapilio = osm_auth.oauth.token
    parsed_data = json.loads(json.dumps(access_token))
    token = parsed_data['user_data']
    if access_token:
        return redirect('https://127.0.0.1:5050/get_my_data/' + token)
    else:
        return redirect('https://127.0.0.1:5050/login')


@app.route('/get_my_data/<user_data>', methods=['GET'])
def get_my_data(user_data):
    user_data = osm_auth.deserialize_data(user_data)
    user_name = user_data['username']
    session['user_name'] = user_name
    return redirect(url_for('display_sequence'))


@app.route('/check-status/<sequence_id>', methods=['GET'])
def check_status(sequence_id):
    status = check_sequence_status(sequence_id)
    return jsonify({"status": status})


# Mapilio Login
@app.route('/mapilio-login', methods=['POST'])
def mapilio_login():
    args = get_args_mapilio(edit_config)
    email = request.form['email'].strip()
    password = request.form['password'].strip()

    username = email.split('@')[0]

    args["user_name"] = username
    args["user_email"] = email
    args["user_password"] = password
    args["gui"] = True
    check_authenticate = authenticator().perform_task(args)

    if check_authenticate['status']:
        return redirect(url_for('display_sequence'))
    else:
        message = check_authenticate['message']
        return render_template('mapilio-login.html', message=message)


@app.route('/mapilio-login-with-osm', methods=['POST'])
def mapilio_login_with_osm():
    token = osm_token_to_mapilio.get('access_token')
    if not token:
        return jsonify({"status": "error", "message": "OSM token not found"}), 400

    resp_osm_login = requests.post(f"{MAPILIO_API_ENDPOINT}/oauth-api/openstreetmap/authenticate",
                                   params={"token": token, "client_id": client_id,
                                           "client_secret": client_secret})

    if resp_osm_login.status_code == 200:
        mapilio_access_token = resp_osm_login.json().get('access_token')
        try:
            resp_mapilio_profile = requests.post(f"{MAPILIO_API_ENDPOINT}/api/function/user_profile/profile/getProfile",
                                                 headers={"Authorization": f"Bearer {mapilio_access_token}"})

            if resp_mapilio_profile.status_code == 200:
                settingsMail = resp_mapilio_profile.json().get('response', {}).get('email')
                settingsUserName = resp_mapilio_profile.json().get('response', {}).get('username')
                settingsUserKey = resp_mapilio_profile.json().get('response', {}).get('id')
                user_upload_token = mapilio_access_token

                with open(MAPILIO_CONFIG_PATH, 'w') as file:
                    file.write(f"[{settingsMail}]\n")
                    file.write(f"SettingsEmail = {settingsMail}\n")
                    file.write(f"SettingsUsername = {settingsUserName}\n")
                    file.write(f"SettingsUserKey = {settingsUserKey}\n")
                    file.write(f"user_upload_token = {user_upload_token}\n")

                return redirect(url_for('display_sequence'))
            else:
                return jsonify({"status": "error", "message": "Failed to get Mapilio profile"}), 500
        except Exception as e:
            return jsonify(
                {"status": "error", "message": "Mapilio authentication failed with OSM", "exception": str(e)}), 500
    else:
        return jsonify({"status": "error", "message": "Mapilio authentication failed with OSM",
                        "status_code": resp_osm_login.status_code}), 500


@app.route('/display-sequence', methods=['GET'])
def display_sequence():
    """
    The page where sequences fetched from Kartaview are shown.
    """
    karta_auth = check_kartaview_authenticate()
    if karta_auth:
        user_name = session.get('user_name') or request.form.get('user_name')
    else:
        return redirect((url_for('kartaview_login_page')))

    MERGED_RESPONSE = os.path.join(os.path.expanduser("~"), ".config", "mapilio", "configs", "MapSyncer",
                                   f"{user_name}_sequences_logs.json")
    check_authenticate = False

    if len(list_all_users()) == 0:
        return render_template('mapilio-login.html', karta_authenticate=True)
    elif len(list_all_users()) == 2:
        status = remove_mapilio_account()
        if status:
            return render_template('mapilio-login.html', karta_authenticate=True)
    else:
        check_authenticate = True

    if check_authenticate:
        try:
            with open(MERGED_RESPONSE, encoding='utf-8') as f:
                response_data = json.load(f)
        except Exception as e:
            print(e)
            response_data = None

        if response_data is None:
            message = "No data available. Press the button below to fetch the sequences."
            return render_template('display-sequence.html', message=message, user_name=user_name)

        download_logs = load_data() or []
        sequence_data = []

        for page_data in response_data.values():
            sequence_data.extend(page_data.get('currentPageItems', []))

        total_sequences = len(sequence_data)
        items_per_page = 39
        current_page = request.args.get('page', 1, type=int)
        start_index = (current_page - 1) * items_per_page
        end_index = min(start_index + items_per_page, total_sequences)

        sequence_data = sequence_data[start_index:end_index]

        for item in sequence_data:
            seq_id = item.get('id')
            log_item = next((log for log in download_logs if log.get('seq_id') == seq_id), None)

            if log_item:
                item['upload_disabled'] = log_item.get('upload_success', False)
                item['download_disabled'] = log_item.get('download_success', False)
            else:
                item['upload_disabled'] = False
                item['download_disabled'] = False

        num_pages = math.ceil(total_sequences / items_per_page)
        return render_template('display-sequence.html', sequence_data=sequence_data, current_page=current_page,
                               num_pages=num_pages, items_per_page=items_per_page, user_name=user_name)


@app.route('/details', methods=['GET', 'POST'])
def details_page():
    """
    Users can check whether the download, upload, and json operations of the sequences are successful or not.
    """
    sequence_filter = 'all'
    download_logs = load_data()

    # GET
    if request.method == 'GET':
        karta_auth = check_kartaview_authenticate()
        if not karta_auth:
            return redirect(url_for('kartaview_login_page'))
        if len(list_all_users()) == 0:
            return render_template('mapilio-login.html')
        elif len(list_all_users()) == 2:
            status = remove_mapilio_account()
            if status:
                return render_template('mapilio-login.html', karta_authenticate=True)
        if download_logs is None:
            message = "No data available. Please check the terminal for further details."
            return render_template('details.html', message=message)

    if request.method == 'POST':
        sequence_filter = request.form['filter']

    filtered_data = []
    for item in download_logs:
        if sequence_filter == 'all' or item.get(sequence_filter):
            filtered_data.append(item)

    if not filtered_data:
        message = "No items found with selected filter."
    else:
        message = None

    return render_template('details.html', data=filtered_data, filter=filter, message=message)


@app.route('/sequence-edit', methods=['GET', 'POST'])
def update_json():
    """
    Changes a requested value from the log file where the download, upload, json data extraction operations
    of the arrays are kept.
    """
    # GET
    if request.method == 'GET':
        karta_auth = check_kartaview_authenticate()
        if not karta_auth:
            return redirect(url_for('kartaview_login_page'))
        if len(list_all_users()) == 0:
            return render_template('mapilio-login.html')
        elif len(list_all_users()) == 2:
            status = remove_mapilio_account()
            if status:
                return render_template('mapilio-login.html', karta_authenticate=True)
        return render_template('sequence-edit.html')

    # POST
    if request.method == 'POST':
        seq_id = request.form.get('seq_id').strip()
        key = request.form.get('key')
        new_value = request.form.get('new_value')

        if not seq_id or not key or new_value not in ['true', 'false']:
            return jsonify({"success": False, "message": "Invalid request data"}), 400

        data = load_data()
        if data is None:
            return jsonify({"success": False, "message": "Log file not found"}), 404

        for item in data:
            if item['seq_id'] == seq_id:
                item[key] = new_value == 'true'
                save_data(data)
                return jsonify({"success": True, "message": "JSON updated successfully"})
    return jsonify({"message": "Sequence ID not found"}), 404


@app.route('/download-sequence', methods=['POST'])
def download_sequence(sequence_id=None):
    """
    Download sequence from Kartaview
    """
    user_name = session.get('user_name')
    response, _ = download_progress_bar()

    if sequence_id is None:
        sequence_id = request.form.get('sequence_id')

    if IMAGES_PATH:
        download_user_images(IMAGES_PATH, user_name, sequence_id)
        return jsonify({"status": "success", "message": "Sequence downloaded successfully"}), 200
    return jsonify({"status": "error", "message": "missing path parameter"}), 400


@app.route('/upload-sequence', methods=['POST'])
def upload_sequence():
    """
    Sequence upload to Mapilio
    """
    sequence_id = request.form.get('sequence_id')
    upload_folder_path = os.path.join(IMAGES_PATH, sequence_id)
    download_logs = load_data()
    for log_entry in download_logs:
        if log_entry["seq_id"] == sequence_id:
            if log_entry["upload_success"]:
                return jsonify({"status": "success", "message": "Sequence already uploaded"}), 200
            else:
                result = upload(upload_folder_path)

                if not result['Success']:
                    print(f"Error occurred while uploading {sequence_id}")
                    return jsonify({"status": "error",
                                    "message": "An error occurred during the upload process. Please check the terminal for further details."}), 500
                else:
                    log_entry["upload_success"] = True
                    save_data(download_logs)
                    uploaded_path = os.path.join(IMAGES_PATH, sequence_id)
                    try:
                        shutil.rmtree(uploaded_path)
                    except OSError as err:
                        print(f"Error: {uploaded_path} could not be deleted. - {err}")
                    return jsonify({"status": "success", "message": "Sequence uploaded successfully"})
    return jsonify({"status": "error", "message": "Sequence not found in log file or sequence folder not found."}), 404


@app.route('/download-progress-bar', methods=['POST'])
def download_progress_bar():
    """
    Progress bar of sequences downloaded from Kartaview
    """
    sequence_id = request.form.get('sequence_id')
    osc_api_instance = OSCApi(OSCAPISubDomain.PRODUCTION)
    photos, error = osc_api_instance.get_photos(sequence_id)
    if error:
        return jsonify({"status": "error", "message": str(error)}), 500

    progress_value = progress.get(sequence_id, 0)
    return jsonify({"status": "success", "photos": len(photos), "progress": progress_value}), 200


@app.route('/get-user-sequences', methods=['POST'])
def get_user_sequences():
    """
    Retrieval of sequences from the user's Kartaview account.
    """
    user_name = session.get('user_name') or request.form.get('user_name')
    osc_api_instance = OSCApi(OSCAPISubDomain.PRODUCTION)
    sequences, error = osc_api_instance.user_sequences(user_name)

    if error:
        return jsonify({"status": "error", "message": str(error)}), 500
    else:
        return jsonify({'status': 'success', 'message': "Sequences successfully fetched"}), 200


@app.route('/get-missing-sequences', methods=['POST'])
def get_missing_sequences():
    user_name = session.get('user_name') or request.form.get('user_name')
    osc_api_instance = OSCApi(OSCAPISubDomain.PRODUCTION)
    sequences, error = osc_api_instance.get_missing_sequences(user_name)
    if error:
        return jsonify({"status": "error", "message": str(error)}), 500
    else:
        return jsonify({'status': 'success', 'message': "Sequences successfully fetched"}), 200


@app.route('/remove-accounts', methods=['GET'])
def remove_accounts():
    """
    Logs out of both Kartaview and Mapilio accounts.
    """
    if os.path.exists(MAPILIO_CONFIG_PATH):
        os.remove(MAPILIO_CONFIG_PATH)
    session.clear()

    return jsonify(success=True), 200


def main():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(CERT_PEM, KEY_PEM)
    webbrowser.open('https://127.0.0.1:5050')
    app.run(host='0.0.0.0', port=5050, threaded=True, debug=False, ssl_context=ssl_context)


if __name__ == '__main__':
    main()
