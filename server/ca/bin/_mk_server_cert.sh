#!/bin/bash

HOST=$1
PRIVATE_KEY=$3
INFO=$2

CA_CERT=$4
CA_CERT_KEY=$5


certtool --generate-certificate \
            --template $INFO \
            --load-privkey $PRIVATE_KEY \
            --load-ca-certificate $CA_CERT \
            --load-ca-privkey $CA_CERT_KEY \
            --outfile $HOST.cert.pem
