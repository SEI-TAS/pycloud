#!/bin/bash

srcdir=$(readlink -m $(dirname $0))
source $srcdir/common

print_help() {
    echo ""
    echo "USAGE: $0 hostname ca ca_key"
    echo
    echo "This script will generate server certificates based on a hostname"
    echo "in the ssdlab.sei.cmu.edu domain and organization"
    echo ""
    exit 0
}

HOST=$1
CA_CERT=$2
CA_CERT_KEY=$3

test -z $HOST && error "You must supply a host"
test -z $CA_CERT &&  error "You must supply a CA"
test -e $CA_CERT || error "CA does not exist"
test -z $CA_CERT_KEY && error "You must supply a CA key"
test -e $CA_CERT_KEY || error "CA key does not exist"

#HOST=$HOST.$DOMAIN

tmp=$(mktemp)
$srcdir/_mk_client_info.sh $HOST > $tmp

echo "Generating private key"
$srcdir/_mk_key.sh $HOST.client.key.pem

echo "Generating certificate"
$srcdir/_mk_cert.sh $HOST $tmp $HOST.client.key.pem $CA_CERT $CA_CERT_KEY $HOST.client.pem
