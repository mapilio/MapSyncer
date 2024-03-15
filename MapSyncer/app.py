import json
import os
import argparse

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

from MapSyncer.components.download import download_user_images, check_sequence_status, progress
from MapSyncer.components.osc_api_gateway import OSCApi
from MapSyncer.components.osc_api_gateway import OSCAPISubDomain


app = Flask(__name__)
parser = argparse.ArgumentParser()
parser.add_argument('--username', type=str, help='Username')
parser.add_argument('--to_path', type=str, help='Path to download images')
args = parser.parse_args()
load_dotenv()
download_logs_path = os.getenv('DOWNLOAD_LOGS_PATH')

def save_data(data):
    try:
        with open(download_logs_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(e)
        return None


def load_data():
    try:
        with open(download_logs_path, encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(e)
        return None

def get_sequences():
    user_name = args.username
    with open(f'.{user_name}_merged_response.json', encoding='utf-8') as f:
        response_data = json.load(f)

    sequence_list = []

    for i in response_data.values():
        for eleman in i['currentPageItems']:
            sequence_list.append(eleman['id'])
    return sequence_list



@app.route('/check-status/<sequence_id>', methods=['GET'])
def check_status(sequence_id):
    status = check_sequence_status(sequence_id)
    return jsonify({"status": status})


@app.route('/', methods=['GET'])
def display_sequence():
    """Displays the sequence data"""
    user_name = args.username

    try:
        with open(f'.{user_name}_merged_response.json', encoding='utf-8') as f:
            response_data = json.load(f)
    except Exception as e:
        print(e)
        response_data = None

    if response_data is None:
        message = "No data available. Please check the terminal for further details."
        return render_template('details.html', message=message)

    download_logs = load_data() or []

    currentPageItems_index = 0
    sequence_data = []
    while str(currentPageItems_index) in response_data:
        sequence_data.extend(response_data[str(currentPageItems_index)]['currentPageItems'])
        currentPageItems_index += 1

    for item in sequence_data:
        seq_id = item.get('id')
        log_item = next((log for log in download_logs if log.get('seq_id') == seq_id), None)

        if log_item:
            item['upload_disabled'] = log_item.get('upload_success', False)
            item['download_disabled'] = log_item.get('download_success', False)
        else:
            item['upload_disabled'] = False
            item['download_disabled'] = False

    return render_template('display-sequence.html', sequence_data=sequence_data)


@app.route('/details', methods=['GET', 'POST'])
def details_page():
    download_logs = load_data()

    if download_logs is None:
        message = "No data available. Please check the terminal for further details."
        return render_template('details.html', message=message)

    sequence_filter = 'all'

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
    if request.method == 'GET':
        return render_template('sequence-edit.html')

    # POST
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
            return jsonify({"message": "JSON updated successfully"})

    return jsonify({"message": "Sequence ID not found"}), 404


@app.route('/download-sequence', methods=['POST'])
def download_sequence(to_path=None, sequence_id=None):
    if to_path is None:
        to_path = args.to_path

    response, _ = download_progress_bar()

    if sequence_id is None:
        sequence_id = request.form.get('sequence_id')

    if to_path:
        download_user_images(to_path, sequence_id)
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "missing to_path parameter"}), 400


@app.route('/upload-sequence', methods=['POST'])
def upload_sequence():
    to_path = args.to_path
    sequence_id = request.form.get('sequence_id')
    upload_folder_path = os.path.join(to_path, sequence_id)
    if not to_path:
        return jsonify({"status": "error", "message": "missing 'to_path' parameter"}), 400
    download_logs = load_data()
    for log_entry in download_logs:
        if log_entry["seq_id"] == sequence_id:
            if log_entry["upload_success"]:
                return jsonify({"status": "success", "message": "Sequence already uploaded"}), 200
            else:
                result = os.system(f"mapilio_kit upload --processed {upload_folder_path}")
                if result != 0:
                    print(f"Error occurred while uploading {sequence_id}")
                    return jsonify({"status": "error",
                                    "message": "An error occurred during the upload process. Please check the terminal for further details."}), 500
                else:
                    log_entry["upload_success"] = True
                    save_data(download_logs)
                    return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Sequence not found in log file or sequence folder not found."}), 404

@app.route('/download-progress-bar', methods=['POST'])
def download_progress_bar():
    sequence_id = request.form.get('sequence_id')
    osc_api_instance = OSCApi(OSCAPISubDomain.PRODUCTION)
    photos, error = osc_api_instance.get_photos(sequence_id)
    if error:
        return jsonify({"status": "error", "message": str(error)}), 500

    progress_value = progress.get(sequence_id, 0)

    return jsonify({"status": "success", "photos": len(photos), "progress": progress_value}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, threaded=True)
