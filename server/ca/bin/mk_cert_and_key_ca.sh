#!/bin/bash

srcdir=$(readlink -m $(dirname $0))
source $srcdir/common

ORG=$1

test -z ORG && error "You must supply an organization"

NAME=certificate_authority

echo "Generating private key"
$srcdir/_mk_key.sh $NAME

TEMP_INFO_FILE=$(mktemp)
$srcdir/_mk_ca_info.sh $ORG > $TEMP_INFO_FILE

echo "Generating certificate"
$srcdir/_mk_cert_self_signed.sh $NAME $TEMP_INFO_FILE

rm TEMP_INFO_FILE
