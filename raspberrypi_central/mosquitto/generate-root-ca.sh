# add "-des3" If you want a password protected key
openssl genrsa -out ./config/certs/rootCA.key 4096

openssl req -x509 -new -nodes -key ./config/certs/rootCA.key -sha256 -days 1024 -out ./config/certs/rootCA.crt
