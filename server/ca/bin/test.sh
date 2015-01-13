#!/bin/bash

srcdir=$(readlink -m $(dirname $0))
source $srcdir/common

ret=$(testing)
echo $ret
