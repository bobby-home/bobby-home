# pull official base image
FROM python:3.8.1

# set work directory
WORKDIR /usr/src/app

# don't generate *.pyc files
ENV PYTHONDONTWRITEBYTECODE 1

# print to stdout without buffering
ENV PYTHONUNBUFFERED 1

RUN apt-get update

# install dependencies
COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt

# copy project
COPY . /usr/src/app/
