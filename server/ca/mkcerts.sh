#!/bin/bash

srcdir=./bin
source $srcdir/common
fqdn="$(hostname --fqdn)"
echo $fqdn

$srcdir/mk_server.sh $fqdn cacert.pem cacert_key.pem
$srcdir/mk_client.sh $fqdn cacert.pem cacert_key.pem
