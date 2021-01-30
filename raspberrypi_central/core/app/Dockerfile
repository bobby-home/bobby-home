# pull official base image
FROM python:3.8.5

ARG USER_ID
ARG GROUP_ID

# add our user with its group
RUN groupadd -f -g $GROUP_ID house && adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID house; \
    mkdir -p /var/lib/house; \
	chown -R house:house /var/lib/house

# set work directory
WORKDIR /usr/src/app

# don't generate *.pyc files
ENV PYTHONDONTWRITEBYTECODE 1

# print to stdout without buffering
ENV PYTHONUNBUFFERED 1

# netcat is not required for alpine images, but debian based yes.
# otherwise "nc" command not found.
# gettext is used by django to extract texts to translate: https://docs.djangoproject.com/en/3.1/topics/i18n/translation/#message-files
# libpq-dev is used for psycopg2-binary, see: https://stackoverflow.com/a/12037133
# gpac is used to convert PiCamera videos h264 to mp4
RUN apt-get update \
    && apt-get install -y libpq-dev netcat gettext gpac

# upgrade python with root user
RUN pip install --upgrade pip

# run everything with this user
USER house

# add pip dependencies folder to PATH
ENV PATH="/home/house/.local/bin:${PATH}"

# install dependencies
COPY requirements.txt /tmp/

# thanks to --user, pip will install everything in user directory ~/.local/bin/
RUN pip install --user --requirement /tmp/requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

ENV MEDIA_FOLDER=/var/lib/house/media
RUN mkdir -p "$MEDIA_FOLDER" && chown -R house:house "$MEDIA_FOLDER" && chmod 700 "$MEDIA_FOLDER"

VOLUME ["/var/lib/house/media"]

# copy project
COPY . /usr/src/app/

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
