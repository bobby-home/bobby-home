FROM rpi_opencv:1.4

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# Install picamera dependencies
RUN apt-get update && apt-get install -y python3-pygame libsdl1.2-dev


# install dependencies via pip
RUN pip install --upgrade pip

COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt


ADD ca.crt /usr/local/share/ca-certificates/ca.cert
RUN chmod 644 /usr/local/share/ca-certificates/ca.cert && update-ca-certificates

# copy project
COPY . /usr/src/app/
