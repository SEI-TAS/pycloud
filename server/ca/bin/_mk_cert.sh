#!/bin/bash

NAME=$1
INFO=$2
CA_CERT=$3
CA_PRIV_KEY=$4

certtool --generate-certificate \
            --template $INFO \
            --load-privkey $NAME.key.pem \
            --load-ca-certificate $CA_CERT \
            --load-ca-privkey $CA_PRIV_KEY \
            --outfile $NAME.certificate.pem
