# MapSyncer

This repository provides a streamlined process for downloading user images from Kartaview and uploading them to Mapilio.<br>

Please, follow the steps below to get started:

## Install dependencies

MapSyncer depends on the following libraries that need to be installed before building it.<br>

* [Mapilio Kit](https://github.com/mapilio/mapilio-kit)
* [Exiftool](https://exiftool.org/install.html)

## Installation

1. Clone the **MapSyncer** repository:

```bash
git clone https://github.com/mapilio/MapSyncer.git
cd MapSyncer
```

2. Create Virtualenv **(Optional)**:

```bash
python -m venv mapsyncer_env

# Ubuntu 
source mapsyncer_env/bin/activate

# Windows
mapsyncer_env/Scripts/activate
```

3. Install the required dependencies:

```bash 
pip install -r requirements.txt
```

## Workflow
The download command follows these steps below:

1. Authenticate the user with OpenStreetMap (OSM) account via Kartaview.
2. Get the list of sequences uploaded by the user.
3. Download all images and metadata for each sequence.
4. Authenticate for Mapilio.
5. You can select the specific sequences you want to upload to Mapilio or all downloaded sequences.
6. And the process ends successfully.

Don't worry, run.py will lead all this for you 💫. 

## Usage

The whole process will take place in one line 

```bash
python run.py
```

Then you can start the whole process by giving the **folder path** where you would like to download your images 💥.


## Clean Up

If you need to remove and uninstall everything except images, please refer to the [Clean Up instructions](CleanUp.md).


## Contributing

If you encounter issues or have suggestions for improvements, please report them on the GitHub repository 🚀.

## License

This project is licensed under the [MIT License](https://github.com/mapilio/MapSyncer?tab=MIT-1-ov-file).

## Contributions and Contact
Feel free to reach out [GitHub Issues]() if you have any questions, contribution idea or need further assistance!<br>

[Mapilio](https://mapilio.com/) is everywhere in the world! 🌍