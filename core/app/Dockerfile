FROM python:3.9.4-slim-buster as base

# do not use slim image to build
# it misses a lot of necessary packages to build pip dependencies (gcc for example).
FROM python:3.9.4 as builder

# libpq-dev is used for psycopg2-binary, see: https://stackoverflow.com/a/12037133
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    build-essential libssl-dev libffi-dev \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# install Rust to have a Rust compiler needed by the python cryptography package.
# use the recommanded way to install Rust in order to ensure we have a recent version.
# more information: https://cryptography.io/en/latest/installation.html
# for arch amd64 not issue because pip does not build cryptography
# but for linux/arm/v7 it does.
RUN curl --proto '=https' --tlsv1.2 -sSf -y https://sh.rustup.rs | sh
RUN pip install --upgrade pip

# add pip dependencies folder to PATH
ENV PATH="/root/.local/bin:${PATH}"
# add rust to PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# for pip cryptography (3.4.5) package.
# was suggested in the build failure message.
# see: https://github.com/docker/compose/issues/8105#issuecomment-775879420
# sadly even with rust downloaded it does not find the Rust compiler,
# and I do not get the time to invesgitate any further the issue.
ENV CRYPTOGRAPHY_DONT_BUILD_RUST 1

COPY requirements.txt /tmp/
RUN pip install --user --requirement /tmp/requirements.txt

# final image
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
# libpq-dev is used by psycopg2
# otherwise: "Error loading psycopg2 module: libpq.so.5: cannot open shared object file: No such file or directory"
# gettext is used by django to extract texts to translate: https://docs.djangoproject.com/en/3.1/topics/i18n/translation/#message-files
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

WORKDIR /usr/src/app

# don't generate *.pyc files
ENV PYTHONDONTWRITEBYTECODE 1

# print to stdout without buffering
ENV PYTHONUNBUFFERED 1

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
