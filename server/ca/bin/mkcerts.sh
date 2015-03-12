#!/bin/bash

$srcdir/mk_cert_and_key.sh server $1
$srcdir/mk_cert_and_key.sh client $1
