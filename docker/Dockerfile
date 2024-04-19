FROM ubuntu:20.04

WORKDIR /app

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    libc-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    python3.9 \
    python3-pip \
    git \
    nano \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1

RUN python3 -m pip install --upgrade pip

RUN python3 -m pip install --upgrade git+https://github.com/mapilio/mapsyncer