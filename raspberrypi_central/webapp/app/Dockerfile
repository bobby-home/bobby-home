# pull official base image
FROM python:3.8.5-slim

# set work directory
WORKDIR /usr/src/app

# don't generate *.pyc files
ENV PYTHONDONTWRITEBYTECODE 1

# print to stdout without buffering
ENV PYTHONUNBUFFERED 1

# netcat is not required for alpine images, but debian based yes.
# otherwise "nc" command not found.
# gettext is used by django to extract texts to translate: https://docs.djangoproject.com/en/3.1/topics/i18n/translation/#message-files
RUN apt-get update \
    && apt-get install -y pipenv netcat gettext

# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

# copy project
COPY . /usr/src/app/

# ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
