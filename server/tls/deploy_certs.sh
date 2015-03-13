#!/bin/bash

# Recreate target folder for the CA certificate.
rm -f -r /etc/pki/CA
mkdir -p /etc/pki/CA

# Copy and set permissions for CA certificate.
cp certificate_authority.certificate.pem /etc/pki/CA/cacert.pem
chmod 444 /etc/pki/CA/cacert.pem

# Recreate target folders for the host certificates and keys.

rm -f -r /etc/pki/libvirt

mkdir -p /etc/pki/libvirt
chmod 755 /etc/pki/libvirt

mkdir -p /etc/pki/libvirt/private
chmod 750 /etc/pki/libvirt/private

# Copy the certificates and private keys.
cp *.client.certificate.pem /etc/pki/libvirt/clientcert.pem
cp *.server.certificate.pem /etc/pki/libvirt/servercert.pem
cp *.client.key.pem /etc/pki/libvirt/private/clientkey.pem
cp *.server.key.pem /etc/pki/libvirt/private/serverkey.pem

# Set proper ownership and permissions.

chgrp kvm /etc/pki/libvirt \
          /etc/pki/libvirt/clientcert.pem \
          /etc/pki/libvirt/servercert.pem \
          /etc/pki/libvirt/private \
          /etc/pki/libvirt/private/clientkey.pem \
          /etc/pki/libvirt/private/serverkey.pem

chmod 440 /etc/pki/libvirt/clientcert.pem \
          /etc/pki/libvirt/servercert.pem \
          /etc/pki/libvirt/private/clientkey.pem \
          /etc/pki/libvirt/private/serverkey.pem
          
# Restart libvirt daemon so it will use the new certificates.
stop libvirt-bin
start libvirt-bin
