import io
import os
import re

import setuptools


def get_long_desc():
    basedir = os.path.abspath(os.path.dirname(__file__))
    with io.open(os.path.join(basedir, "README.md"), encoding="utf-8") as f:
        return f.read()


def get_version():
    cwd = os.path.abspath(os.path.dirname(__file__))
    current_version = os.path.join(cwd, "MapSyncer", "components", "version_.py")
    with io.open(current_version, encoding="utf-8") as f:
        return re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', f.read(), re.M).group(1)


# TODO: This part will be removed with an alternative solution.
INSTALL_REQUIRES = [
    'mapilio-kit',
    'ExifRead',
    'calculation-mapilio==0.1.39',
    'requests_oauthlib',
    'imagesize',
    'setuptools',
    'psutil',
    'flask',
    'python-dotenv',
    'osm-login-python'
]

setuptools.setup(
    name="mapsyncer",
    version=get_version(),
    author="Mapilio",
    description="A toolkit to download and upload the data from KartaView to Mapilio",
    long_description=get_long_desc(),
    long_description_content_type='text/markdown',
    url="https://github.com/mapilio/MapSyncer",
    packages=setuptools.find_packages(),
    package_data={
        'MapSyncer': [
            'static/*',
            'templates/*'
        ]
    },
    license='MIT License',
    python_requires='>=3.6',
    install_requires=INSTALL_REQUIRES,
    entry_points={
        "console_scripts": [
            "RunMapSyncer=MapSyncer.app:main"
        ]
    }
)
