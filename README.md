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
1. Authenticate for OpenStreetMap.
2. Authenticate for Mapilio.
3. Get the list of sequences uploaded by the user.
4. Download all images and metadata for each sequence.
5. You can select specific sequences or all downloaded sequences that you want to upload to Mapilio.
6. And the process ends successfully.

Don't worry, the RunMapSyncer command will check and do all these operations. 💫


## Install dependencies

MapSyncer depends on the following libraries that need to be installed before building it.<br>

* [Exiftool](https://exiftool.org/install.html)


## Pip Installation and Usage

<b>Note:</b> To install MapSyncer, you'll need to have Python and Pip installed on your system. Ensure you have Python version above <b>3.6</b> but below <b>3.12</b>. If you meet these criteria, please run the following commands:

```bash
# Installation
pip install mapsyncer

# CLI Usage
RunMapSyncer
```
<p>Once RunMapSyncer is running, https://127.0.0.1:5050 will open in your default web browser.</p>
<p>
   When accessing the provided address, you may encounter a security warning stating <b>"Your connection is not private"</b> in your web browser. To proceed, please click the <b>"Advanced"</b> button and select the option to continue to the site. This warning is due to the SSL certificate currently being in the process of approval and will be validated shortly.
</p>

## Manual Installation

1. Clone the **MapSyncer** repository:

```bash
git clone https://github.com/mapilio/MapSyncer.git
cd MapSyncer
```

2. Create Virtualenv **(Optional)**:

```bash
python -m venv mapsyncer_env

# Ubuntu & MacOS
source mapsyncer_env/bin/activate

# Windows
mapsyncer_env/Scripts/activate
```

3. Install the required dependencies:

```bash 
pip install -e .
```

## Usage

The whole process will take place in one line 

```bash
RunMapSyncer
```
Once RunMapSyncer is running, https://127.0.0.1:5050 will open in your default web browser.


## Clean Up

If you need to remove and uninstall everything except images, please refer to the [Clean Up instructions](CleanUp.md).


## Contributing

If you encounter issues or have suggestions for improvements, please report them on the GitHub repository 🚀.

## License

This project is licensed under the [MIT License](https://github.com/mapilio/MapSyncer?tab=MIT-1-ov-file).

## Contributions and Contact
Feel free to reach out [GitHub Issues]() if you have any questions, contribution idea or need further assistance!<br>

[Mapilio](https://mapilio.com/) is everywhere in the world! 🌍
