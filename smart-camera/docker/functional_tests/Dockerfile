FROM python:3.10-slim-buster

WORKDIR /usr/src/app

COPY ./requirements.test.txt /tmp/requirements.txt
RUN pip install --user --requirement /tmp/requirements.txt

ENV MEDIA_FOLDER=/var/lib/camera/media

COPY ./functional_tests /usr/src/app
