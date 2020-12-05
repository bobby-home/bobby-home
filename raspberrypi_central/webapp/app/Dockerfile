# pull official base image
FROM python:3.8.5-slim

ARG USER_ID
ARG GROUP_ID

# add our user with its group
RUN groupadd -f -g $GROUP_ID user && adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID user

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

# upgrade python with root user
RUN pip install --upgrade pip

# run everything with this user
USER user

# add pip dependencies folder to PATH
ENV PATH="/home/user/.local/bin:${PATH}"

# install dependencies
COPY requirements.txt /tmp/

# thanks to --user, pip will install everything in user directory ~/.local/bin/
RUN pip install --user --requirement /tmp/requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

# copy project
COPY . /usr/src/app/

# ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
