<div align="center">
   <a href="https://mapilio.com/" target="_blank">
   <img width="100%" src="https://github.com/mapilio/MapSyncer/blob/main/docs/assets/mapsyncer-banner2.png"></a>
</div>

<div align="center">
    <a href="https://github.com/mapilio/MapSyncer/actions/workflows/ci.yml">
      <img src="https://github.com/mapilio/MapSyncer/actions/workflows/ci.yml/badge.svg" alt="MapSyncer CI"></a>
   <a href="https://github.com/mapilio/MapSyncer/blob/main/LICENSE">
      <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="mit-license"></a>
   <a href="https://discord.gg/uhsR97sF">
      <img src="https://img.shields.io/discord/1028938271453089852?logo=discord" alt="discord-badge"></a>
   <a href="https://pypi.org/project/mapilio-kit/">
      <img src="https://img.shields.io/pypi/v/MapSyncer?color=purple" alt="PyPI version"></a>
   <a href="">
      <img src="https://img.shields.io/github/stars/mapilio/MapSyncer?color=blue" alt="stars"></a>
   <a href="">
      <img src="https://img.shields.io/github/contributors/mapilio/MapSyncer?color=orange" alt="contributors"></a>
   <a href="">
      <img src="https://img.shields.io/github/issues-raw/mapilio/MapSyncer?color=darkred" alt="issue-counter"></a>
   <a href="">
      <img src="https://img.shields.io/github/release-date-pre/mapilio/MapSyncer?color=green" alt="release-date-badge"></a>
   <a href="">
      <img src="https://img.shields.io/github/last-commit/mapilio/MapSyncer?color=D60051" alt="last-commit-badge"></a>
</div>

# MapSyncer

This repository provides a streamlined process for downloading user images from Kartaview and uploading them to Mapilio.<br>

Please, follow the steps below to get started:


## Workflow
The download command follows these steps below:

1. Authenticate the user with OpenStreetMap (OSM) account via Kartaview.
2. Get the list of sequences uploaded by the user.
3. Download all images and metadata for each sequence.
4. Authenticate for Mapilio.
5. You can select the specific sequences you want to upload to Mapilio or all downloaded sequences.
6. And the process ends successfully.

Don't worry, run.py will lead all this for you 💫. 


## Install dependencies

MapSyncer depends on the following libraries that need to be installed before building it.<br>

* [Mapilio Kit](https://github.com/mapilio/mapilio-kit) `In case you would like to follow the manual way you should install mapilio-kit manually.`
* [Exiftool](https://exiftool.org/install.html)


## Pip Installation and Usage

You may simply install and use the MapSyncer by using these commands below;

```bash
# Installation
pip install mapsyncer

# CLI Usage
RunMapSyncer
```

## Manual Installation

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

## Usage

The whole process will take place in one line 

```bash
cd MapSyncer

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
