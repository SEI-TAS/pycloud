#!/bin/bash

srcdir=$(readlink -m $(dirname $0))
source $srcdir/common

NAME=$1
INFO_FILE=$2

mkdir -p $OUTPUT_FOLDER

certtool --generate-self-signed \
            --template $INFO_FILE \
            --load-privkey $CA_KEY_FOLDER/$NAME.key.pem \
            --outfile $OUTPUT_FOLDER/$NAME.certificate.pem
