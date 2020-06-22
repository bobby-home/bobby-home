# add "-des3" If you want a password protected key
# CERTS_FOLDER="$PWD/../config/mosquitto/certs"
# CA_KEY=$CERTS_FOLDER/rootCA.key
# CA_CRT=$CERTS_FOLDER/rootCA.crt

# echo "Generate rootCA.key"
# openssl genrsa -out $CA_KEY 4096

# echo "Generate rootCA.crt"
# openssl req -x509 -new -nodes -key $CA_KEY -sha256 -days 1024 -out $CA_CRT
