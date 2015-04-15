#!/bin/bash

srcdir=$(readlink -m $(dirname $0))

chmod ugo+x ./bin/*.*

$srcdir/bin/mk_cert_and_key.sh server $1
$srcdir/bin/mk_cert_and_key.sh client $1
