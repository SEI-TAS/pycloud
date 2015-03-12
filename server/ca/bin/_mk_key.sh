#!/bin/bash

srcdir=$(readlink -m $(dirname $0))
source $srcdir/common

NAME=$1
FOLDER=$2

(umask 277 && certtool --generate-privkey > $FOLDER/$NAME.key.pem)
