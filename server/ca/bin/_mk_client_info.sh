#!/bin/bash

srcdir=$(readlink -m $(dirname $0))
source $srcdir/common

host=$1

echo "country = $COUNTRY"
echo "state = $STATE"
echo "locality = $LOCALITY"
echo "organization = $ORG"
echo "cn = $host"
echo "tls_www_client"
echo "encryption_key"
echo "signing_key"
