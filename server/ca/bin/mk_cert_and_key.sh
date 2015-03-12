#!/bin/bash

srcdir=$(readlink -m $(dirname $0))
source $srcdir/common

TYPE=$1
HOST=$2
CA_CERT=$3
CA_PRIV_KEY=$4

ORG=$5
COUNTRY=$6
STATE=$7
LOCALITY=$8

test -z $HOST && error "You must supply a host"
test -z $CA_CERT &&  error "You must supply a CA"
test -e $CA_CERT || error "CA does not exist"
test -z $CA_CERT_KEY && error "You must supply a CA key"
test -e $CA_CERT_KEY || error "CA key does not exist"
test -z $HOST && error "You must supply an organization"

NAME=$HOST.$TYPE

echo "Generating private key"
$srcdir/_mk_key.sh $NAME

TEMP_INFO_FILE=$(mktemp)
$srcdir/_mk_$TYPE_info.sh $HOST $ORG $COUNTRY $STATE $LOCALITY > $TEMP_INFO_FILE

echo "Generating certificate"
$srcdir/_mk_cert.sh $NAME $TEMP_INFO_FILE $CA_CERT $CA_PRIV_KEY

rm TEMP_INFO_FILE
