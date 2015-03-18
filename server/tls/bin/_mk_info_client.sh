#!/bin/bash

HOST=$1
ORG=$2
COUNTRY=$3
STATE=$4
LOCALITY=$5

echo "country = $COUNTRY"
echo "state = $STATE"
echo "locality = $LOCALITY"
echo "organization = $ORG"
echo "cn = $HOST"
echo "tls_www_client"
echo "encryption_key"
echo "signing_key"
