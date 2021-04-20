FROM smart-camera_camera:latest

USER root


RUN apt-get -y update

RUN apt-get -y install curl git libtinfo-dev build-essential wget unzip
# libtinfo-dev used by vim compile. Otherwise: "No Terminal Library Found"
RUN wget https://github.com/vim/vim/archive/refs/tags/v8.2.2739.zip \
  && unzip v8.2.2739 \
  && cd vim-8.2.2739 \
  && cd src \
  ./configure && make && make install

USER camera

# coc vim needs a recent nodejs version. It takes the latest here.
RUN /bin/bash -c "curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.38.0/install.sh | bash \
  && source /home/camera/.nvm/nvm.sh \
  && nvm install node \
  && nvm use default && node -v"

ENTRYPOINT []
