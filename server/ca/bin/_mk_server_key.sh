#!/bin/bash

srcdir=$(readlink -m $(dirname $0))
source $srcdir/common

host=$1

(umask 277 && certtool --generate-privkey > $host.server.key.pem)
