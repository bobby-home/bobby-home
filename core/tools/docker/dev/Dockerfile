FROM core_web:latest

USER root

# already done in base image.
# issue: cannot do anything here: permission defined
# because it runs as a user and not root.
RUN apt-get -y update
RUN apt-get -y install wget nodejs npm
RUN wget https://github.com/vim/vim/archive/refs/tags/v8.2.2739.zip \
  && unzip v8.2.2739 \
  && cd vim-8.2.2739 \
  && cd src \
  ./configure && make && make install

RUN git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim

# next step: add .vimrc through a volume
# so the user could mount its own vimrc file !
COPY .vimrc /root/.vimrc
RUN vim +PluginInstall +qall

#RUN vim :PluginInstall 
# I don't know why, it does not work. No error,just blocks.
RUN vim +CocInstall coc-tsserver coc-json coc-html coc-css coc-pyright +qall

#COPY ./vim_entrypoint.sh /usr/src/app/vim_entrypoint.sh
#ENTRYPOINT ["/usr/src/app/vim_entrypoint.sh"]

ENTRYPOINT []
