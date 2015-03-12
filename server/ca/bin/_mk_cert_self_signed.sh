#!/bin/bash

NAME=$1
INFO=$2

certtool --generate-self-signed \
            --template $INFO \
            --load-privkey $NAME.key.pem \
            --outfile $NAME.certificate.pem
