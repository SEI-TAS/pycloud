#!/bin/bash

srcdir=$(readlink -m $(dirname $0))
source $srcdir/common

$srcdir/mk_server.sh $1 $2 $3
$srcdir/mk_client.sh $1 $2 $3
