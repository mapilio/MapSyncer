import os

DOWNLOAD_LOGS = os.path.join(os.path.expanduser("~"), ".config", "mapilio", "configs", "MapSyncer",
                             "download_logs.json")

IMAGES_PATH = os.path.join(os.path.expanduser("~"), ".cache", "mapilio", "MapSyncer",
                           "images")

CERT_PEM = os.path.join(os.path.expanduser("~"), ".config", "mapilio", "configs", "MapSyncer",
                        "cert.pem")

KEY_PEM = os.path.join(os.path.expanduser("~"), ".config", "mapilio", "configs", "MapSyncer",
                       "key.pem")

MAPILIO_CONFIG_PATH = os.getenv(
    "MAPILIO_CONFIG_PATH",
    os.path.join(
        os.path.expanduser("~"),
        ".config",
        "mapilio",
        "configs",
        "CLIENT_USERS",
    ),
)

MAPILIO_API_ENDPOINT = "https://end.mapilio.com"
client_id = 8
client_secret = "7TccnOQOdxnUIFgOjFiotiuFC4lWQhMeilddgxJJ"