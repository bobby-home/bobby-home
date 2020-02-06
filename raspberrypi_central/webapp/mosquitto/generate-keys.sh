#!/bin/sh
# usage: <script.sh> <client|server>
# generate keys for server or for client. 

#Create CA key-pair and server key-pair signed by CA

CERTS_FOLDER="$PWD/../config/mosquitto/certs"

CA_KEY=$CERTS_FOLDER/rootCA.key
CA_CRT=$CERTS_FOLDER/rootCA.crt

SERVER_KEY=$CERTS_FOLDER/server.key
SERVER_CSR=$CERTS_FOLDER/server.csr
SERVER_CRT=$CERTS_FOLDER/server.crt

keybits=2048
default_digest="-sha256"
days=365

#Important: Please mind that while creating the signign request is important to specify
#the Common Name providing the IP address or domain name for the service,
#otherwise the certificate cannot be verified.

# If you generate the csr in this way, openssl will ask you questions about the certificate to generate like the organization details and the Common Name (CN) that is the web address you are creating the certificate for, e.g mydomain.com.
SUBJ="/C=FR/ST=Occitanie/L=Toulouse/O=Mx home Security/OU=Security/CN=$(hostname)/emailAddress=contact@maxime-moreau.fr"

kind="${1:-server}"

CLIENT='client'

if [ $kind == 'server' ]; then
    if [ ! -d "$CERTS_FOLDER" ]; then
        echo "Creating the $CERTS_FOLDER folder."
        mkdir $CERTS_FOLDER
    fi

    if [ ! -f "$CA_KEY" ]; then
        # Create Root CA
        echo "Creating the Root CA $CA_KEY"
        openssl genrsa -des3 -out $CA_KEY 2048
    fi

    # Create and self sign the Root Certificate with the CA Key
    if [ ! -f "$CA_CRT" ]; then
        echo "Creating the Root Certificate and sign it $CA_CRT"
        # openssl req -x509 -new -nodes -key $CA_KEY -sha256 -days 1024 -out $CA_CRT
        openssl req -newkey rsa:${keybits} -x509 -nodes $default_digest -days $days -extensions v3_ca -keyout $CA_KEY -out $CA_CRT -subj "$SUBJ"
        openssl x509 -in $CA_CRT -nameopt multiline -subject -noout
    fi

    # Create a server certificate
    if [ ! -f $SERVER_KEY ]; then
        echo "Creating the server certificate $SERVER_KEY"

        openssl genrsa -out $SERVER_KEY $keybits

        # Create the signing (self-signed certificate)
        echo "Creating the CSR $SERVER_CSR"
        openssl req -new $default_digest \
            -key $SERVER_KEY \
            -out $SERVER_CSR \
            -subj "$SUBJ"

        # openssl x509 -req $defaultmd \
        #     -in $SERVER_CSR \
        #     -CA $CA_KEY \
        #     -CAkey $SERVER_KEY \
        #     -CAcreateserial \
        #     -CAserial "${DIR}/ca.srl" \
        #     -out $SERVER.crt \
        #     -days $days \
        #     -extfile ${CNF} \
        #     -extensions JPMextensions

        openssl x509 -req -in $SERVER_CSR -CA $CA_CRT -CAkey $CA_KEY -CAcreateserial -out $SERVER_CRT -days $days $default_digest
        openssl x509 -in $SERVER_CRT -text -noout

        #TODO: chmod security!
    fi
else

    if [ ! -f $CLIENT.key ]; then
        openssl genrsa -out $CLIENT.key $keybits
        openssl req -new -key $CLIENT.key -out $CLIENT.csr -subj "$SUBJ"
        openssl req -in $CLIENT.csr -noout -text

        openssl x509 -req -CA $CA_CRT -CAkey $CA_KEY -CAcreateserial -in $CLIENT.csr -out $CLIENT.crt
        openssl x509 -in client.crt -text -noout
    fi
fi
