#!/bin/bash

srcdir=$(readlink -m $(dirname $0))
source $srcdir/common

host=$1

echo "organization = $ORG"
echo "cn = $host"
echo "tls_www_server"
echo "encryption_key"
echo "signing_key"
