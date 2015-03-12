#!/bin/bash

$srcdir/mk_cert_and_key.sh server $1 $2 $3 $4 $5 $6 $7
$srcdir/mk_cert_and_key.sh client $1 $2 $3 $4 $5 $6 $7
