# pull official base image
FROM python:3.8.1

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# netcat is not required for alpine images, but debian based yes.
# otherwise "nc" command not found.
RUN apt-get update \
    && apt-get install -y pipenv netcat

# install dependencies
RUN pip install --upgrade pip
COPY ./Pipfile /usr/src/app/Pipfile
RUN pipenv install

# copy project
COPY . /usr/src/app/
