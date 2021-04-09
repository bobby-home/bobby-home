FROM python:3.9.4-slim-buster as base

FROM base as builder
# upgrade python with root user
RUN pip install --upgrade pip

# install dependencies
COPY requirements.txt /tmp/

# add pip dependencies folder to PATH
ENV PATH="/root/.local/bin:${PATH}"

# thanks to --user, pip will install everything in user directory ~/.local/bin/
RUN pip install --user --requirement /tmp/requirements.txt

FROM base
ARG USER_ID
ARG GROUP_ID

# add our user with its group
RUN groupadd -f -g $GROUP_ID house && adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID house; \
    mkdir -p /var/lib/house; \
	chown -R house:house /var/lib/house

COPY --from=builder /root/.local /home/house/.local
RUN chown -R house:house /home/house/.local

# add pip dependencies folder to PATH
ENV PATH="/home/house/.local/bin:${PATH}"

# netcat is not required for alpine images, but debian based yes.
# otherwise "nc" command not found.
# gettext is used by django to extract texts to translate: https://docs.djangoproject.com/en/3.1/topics/i18n/translation/#message-files
# libpq-dev is used for psycopg2-binary, see: https://stackoverflow.com/a/12037133
# only worker: gpac is used to convert PiCamera videos h264 to mp4
# only worker: rsync is used to retrieve videos
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    gettext \
    gpac \
    libpq-dev \
    netcat \
    rsync \
    && rm -rf /var/lib/apt/lists/*
# set work directory
WORKDIR /usr/src/app

# don't generate *.pyc files
ENV PYTHONDONTWRITEBYTECODE 1

# print to stdout without buffering
ENV PYTHONUNBUFFERED 1

# for pip cryptography (3.4.5) package.
# was suggested in the build failure message.
# see: https://github.com/docker/compose/issues/8105#issuecomment-775879420
ENV CRYPTOGRAPHY_DONT_BUILD_RUST 1

USER house

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

ENV MEDIA_FOLDER=/var/lib/house/media
ENV VIDEO_FOLDER=/var/lib/house/video
RUN mkdir -p "$MEDIA_FOLDER" && chown -R house:house "$MEDIA_FOLDER" && chmod 700 "$MEDIA_FOLDER" \
    && mkdir -p /home/house/.ssh && chown -R house:house /home/house/.ssh \
    && mkdir -p "$VIDEO_FOLDER" && chown -R house:house "$VIDEO_FOLDER"

VOLUME ["/var/lib/house/media"]

# copy project
COPY . /usr/src/app/

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
