FROM mxmaxime/rpi4-opencv:0.0.2

ARG USER_ID
ARG GROUP_ID

RUN groupadd -f -g $GROUP_ID camera && adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID camera; \
    mkdir -p /var/lib/camera; \
    chown -R camera:camera /var/lib/camera

# to have access to input camera and output audio on the RaspberryPi.
RUN usermod -aG video camera && usermod -aG audio camera

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install picamera dependencies & pygame python binding.
# libsdl1.2-dev is for pygame
RUN apt-get update && apt-get install -y netcat libsdl1.2-dev libsdl-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsmpeg-dev libportmidi-dev libavformat-dev libswscale-dev

# install dependencies via pip
RUN pip install --upgrade pip

ENV READTHEDOCS True

USER camera

# add pip dependencies folder to PATH
ENV PATH="/home/camera/.local/bin:${PATH}"

COPY requirements.txt /tmp/
RUN pip install --user --requirement /tmp/requirements.txt

RUN dpkgArch="$(dpkg --print-architecture)"; \
    case "${dpkgArch##*-}" in \
        armv7) tfLiteRuntime='https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp37-cp37m-linux_armv7l.whl';; \
        armhf) tfLiteRuntime='https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp37-cp37m-linux_armv7l.whl';; \
        amd64) tfLiteRuntime='https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp37-cp37m-linux_x86_64.whl';; \
        *) echo >&2; echo >&2 "error: current architecture ($dpkgArch) is not supported." ;; \
    esac; \
    pip install $tfLiteRuntime

ENV MEDIA_FOLDER=/var/lib/camera/media
RUN mkdir -p "$MEDIA_FOLDER" && chown -R camera:camera "$MEDIA_FOLDER" && chmod 700 "$MEDIA_FOLDER"

ENV TF_MODELS_FOLDER=/var/lib/camera/tf-models
RUN mkdir -p "$TF_MODELS_FOLDER" && chown -R camera:camera "$TF_MODELS_FOLDER" && chmod 700 "$TF_MODELS_FOLDER"

VOLUME ["/var/lib/camera/media", "/var/lib/camera/tf-models"]

# ADD ca.crt /usr/local/share/ca-certificates/ca.cert
# RUN chmod 644 /usr/local/share/ca-certificates/ca.cert && update-ca-certificates

COPY . /usr/src/app/

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

