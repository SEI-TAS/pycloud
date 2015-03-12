#!/bin/bash

chmod ugo+x ./bin/*.*

$srcdir/bin/mk_cert_and_key_ca.sh $1 $2 $3 $4
