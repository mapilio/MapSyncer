# MapSyncer

This repository provides a streamlined process for downloading user images from Kartaview and uploading them to Mapilio.<br>
Follow the steps below to get started:

## Install dependencies

From the link [here](https://github.com/mapilio/mapilio-kit), complete the Getting Started section to get the Mapilio Kit working.<br>

* [Mapilio Kit](https://github.com/mapilio/mapilio-kit)
* [Exiftool](https://exiftool.org/install.html)
* [FFmpeg](https://ffmpeg.org/download.html)

## Installation

1. Clone the **MapSyncer** repository:
```
git clone https://github.com/mapilio/MapSyncer.git
cd MapSyncer
```
2. Create Virtualenv **(Optional)**:
```
python -m venv mapsyncer_env

# Ubuntu 
source mapsyncer_env/bin/activate
# Windows
mapsyncer_env/Scripts/activate
```


3. Install the required dependencies:
```
pip install -r requirements.txt
```

## Workflow
The download command follows these steps:

1. Authenticate the user with OpenStreetMap (OSM) account via Kartaview.
2. Get the list of sequences uploaded by the user.
3. Download all images and metadata for each sequence.
4. Authenticate for Mapilio.
5. You can select the specific sequences you want to upload to Mapilio or all downloaded sequences.
6. And the process ends successfully.

Don't worry, run.py will lead all this for you 💫. 

## Usage

The whole process will take place in one line 

```
python run.py
```

Then you can start the whole process by giving the folder path where you want to download your images 💥.

### Contributing

If you encounter issues or have suggestions for improvements, please report them on the GitHub repository 🚀.

### License

This project is licensed under the MIT License.

Feel free to reach out if you have any questions or need further assistance!<br>
Mapilio is everywhere in the world! 🌍