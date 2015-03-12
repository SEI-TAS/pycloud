#!/bin/bash

srcdir=$(readlink -m $(dirname $0))
source $srcdir/common

chmod ugo+x ./bin/*.*

$srcdir/bin/mk_ca_cert_and_key.sh $1 $2 $3 $4
