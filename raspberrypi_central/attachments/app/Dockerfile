FROM mxmaxime/rpi4-opencv:latest

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# Install picamera dependencies & pygame python binding.
RUN apt-get update && apt-get install -y netcat libsdl1.2-dev libsdl-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsmpeg-dev libportmidi-dev libavformat-dev libswscale-dev


# install dependencies via pip
RUN pip install --upgrade pip

ENV READTHEDOCS True

COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt
# RUN pip install https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp37-cp37m-linux_armv7l.whl
RUN pip install https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp37-cp37m-linux_x86_64.whl


# ADD ca.crt /usr/local/share/ca-certificates/ca.cert
# RUN chmod 644 /usr/local/share/ca-certificates/ca.cert && update-ca-certificates

# copy project
COPY . /usr/src/app/
