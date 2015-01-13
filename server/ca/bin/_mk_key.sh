#!/bin/bash

srcdir=$(readlink -m $(dirname $0))
source $srcdir/common

OUT_FILE=$1

(umask 277 && certtool --generate-privkey > $OUT_FILE)
