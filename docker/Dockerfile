FROM python:3.9

WORKDIR /app

# Update and install necessary dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    libc-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade git+https://github.com/mapilio/MapSyncer.git

CMD ["RunMapSyncer"]
