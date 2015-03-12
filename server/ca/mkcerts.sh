#!/bin/bash

chmod ugo+x ./bin/*.*

$srcdir/bin/mkcerts.sh $1
