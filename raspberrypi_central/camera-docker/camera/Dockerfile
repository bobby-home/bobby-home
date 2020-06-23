FROM rpi_opencv:1.4

# set work directory
WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y python3-pygame libsdl1.2-dev

RUN pip install picamera

# copy project
COPY . /usr/src/app/
