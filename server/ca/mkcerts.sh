#!/bin/bash

srcdir=$(readlink -m $(dirname $0))
source $srcdir/bin/common
fqdn="$(hostname --fqdn)"
echo $fqdn

bash $srcdir/bin/mk_server.sh $fqdn cacert.pem cacert_key.pem
bash $srcdir/bin/mk_client.sh $fqdn cacert.pem cacert_key.pem
