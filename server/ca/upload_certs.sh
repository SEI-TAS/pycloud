#!/bin/bash

CLOUDLET_HOST=$1
CLOUDLET_USER=$2

scp certificate_authority.certificate.pem $CLOUDLET_USER@$CLOUDLET_HOST:/tmp
scp CLOUDLET_HOST.server.certificate.pem $CLOUDLET_USER@$CLOUDLET_HOST:/tmp
scp CLOUDLET_HOST.server.key.pem $CLOUDLET_USER@$CLOUDLET_HOST:/tmp
scp CLOUDLET_HOST.client.certificate.pem $CLOUDLET_USER@$CLOUDLET_HOST:/tmp
scp CLOUDLET_HOST.client.key.pem $CLOUDLET_USER@$CLOUDLET_HOST:/tmp
scp deploy_certs.sh $CLOUDLET_USER@$CLOUDLET_HOST:/tmp
