#!/bin/bash

srcdir=./bin
source $srcdir/common

$srcdir/mk_server.sh $1 cacert.pem cacert_key.pem
$srcdir/mk_client.sh $1 cacert.pem cacert_key.pem
