#!/bin/bash

print_help() {
    echo ""
    echo "USAGE: $0 organization country state locality"
    echo
    echo "This script will generate a CA certificate and key for the given organization"
    echo ""
    exit 0
}

srcdir=$(readlink -m $(dirname $0))
source $srcdir/common

ORG=$1
COUNTRY=$2
STATE=$3
LOCALITY=$4

test -z ORG && error "You must supply an organization"
test -z COUNTRY && error "You must supply a country"
test -z STATE && error "You must supply a state"
test -z LOCALITY && error "You must supply a locality"

# Store org info.
rm -f ORG_INFO_FILE
touch ORG_INFO_FILE
echo "ORG=$ORG" > ORG_INFO_FILE
echo "COUNTRY=$COUNTRY" > ORG_INFO_FILE
echo "STATE=$STATE" > ORG_INFO_FILE
echo "LOCALITY=$LOCALITY" > ORG_INFO_FILE

NAME=certificate_authority

echo "Generating private key"
$srcdir/_mk_key.sh $NAME $CA_KEY_FOLDER

TEMP_INFO_FILE=$(mktemp)
$srcdir/_mk_ca_info.sh $ORG > $TEMP_INFO_FILE

echo "Generating certificate"
$srcdir/_mk_ca_cert_self_signed.sh $NAME $TEMP_INFO_FILE

rm TEMP_INFO_FILE
