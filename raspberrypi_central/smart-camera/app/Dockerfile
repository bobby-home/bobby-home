FROM mxmaxime/rpi4-opencv:0.0.2

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

COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt

RUN dpkgArch="$(dpkg --print-architecture)"; \
    case "${dpkgArch##*-}" in \
        armv7) tfLiteRuntime='https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp37-cp37m-linux_armv7l.whl';; \
        armhf) tfLiteRuntime='https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp37-cp37m-linux_armv7l.whl';; \
        amd64) tfLiteRuntime='https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp37-cp37m-linux_x86_64.whl';; \
        *) echo >&2; echo >&2 "error: current architecture ($dpkgArch) is not supported." ;; \
    esac; \
    pip install $tfLiteRuntime

# ADD ca.crt /usr/local/share/ca-certificates/ca.cert
# RUN chmod 644 /usr/local/share/ca-certificates/ca.cert && update-ca-certificates

COPY . /usr/src/app/
