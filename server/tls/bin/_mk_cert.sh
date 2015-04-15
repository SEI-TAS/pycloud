#!/bin/bash

srcdir=$(readlink -m $(dirname $0))
source $srcdir/common

NAME=$1
INFO_FILE=$2
CA_CERT=$3
CA_PRIV_KEY=$4

mkdir -p $OUTPUT_FOLDER

certtool --generate-certificate \
            --template $INFO_FILE \
            --load-privkey $OUTPUT_FOLDER/$NAME.key.pem \
            --load-ca-certificate $CA_CERT \
            --load-ca-privkey $CA_PRIV_KEY \
            --outfile $OUTPUT_FOLDER/$NAME.certificate.pem
