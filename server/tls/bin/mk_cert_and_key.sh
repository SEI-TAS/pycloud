#!/bin/bash

print_help() {
    echo ""
    echo "USAGE: $0 hostname"
    echo
    echo "This script will generate server or client certificates based on a hostname"
    echo "in the organization defined when creating the CA"
    echo ""
    exit 0
}

srcdir=$(readlink -m $(dirname $0))
source $srcdir/common

TYPE=$1
HOST=$2

CA_CERT=$OUTPUT_FOLDER/certificate_authority.certificate.pem
CA_PRIV_KEY=$CA_KEY_FOLDER/certificate_authority.key.pem

test -z $HOST && error "You must supply a host"
test -e $CA_CERT || error "CA does not exist"
test -e $CA_PRIV_KEY || error "CA key does not exist"
test -e $ORG_INFO_FILE || error "Information file about organization does not exist"

# Load organizational info: ORG, COUNTRY, STATE, LOCALITY
srcdir=$(readlink -m $(dirname $0))
source $ORG_INFO_FILE

NAME=$HOST.$TYPE

echo "Generating private key"
$srcdir/_mk_key.sh $NAME $OUTPUT_FOLDER

TEMP_INFO_FILE=$(mktemp)
$srcdir/_mk_$TYPE_info.sh $HOST $ORG $COUNTRY $STATE $LOCALITY > $TEMP_INFO_FILE

echo "Generating certificate"
$srcdir/_mk_cert.sh $NAME $TEMP_INFO_FILE $CA_CERT $CA_PRIV_KEY

rm $TEMP_INFO_FILE
