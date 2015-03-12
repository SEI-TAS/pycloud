#!/bin/bash

chmod ugo+x ./bin/*.*

$srcdir/bin/mkcerts.sh $1 $2 $3 $4 $5 $6 $7
