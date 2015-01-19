#!/bin/bash

srcdir=$(readlink -m $(dirname $0))
source $srcdir/bin/common
fqdn="$(hostname --fqdn)"
echo $fqdn

chmod ug+x ./bin/*.*

$srcdir/bin/mk_server.sh $fqdn cacert.pem cacert_key.pem
$srcdir/bin/mk_client.sh $fqdn cacert.pem cacert_key.pem
