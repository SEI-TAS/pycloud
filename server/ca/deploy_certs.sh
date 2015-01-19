#!/bin/bash
rm -r /etc/pki/libvirt

mkdir /etc/pki/libvirt
chmod 755 /etc/pki/libvirt

mkdir -p /etc/pki/libvirt/private
chmod 750 /etc/pki/libvirt/private

cp *.client.pem /etc/pki/libvirt/clientcert.pem
cp *.server.pem /etc/pki/libvirt/servercert.pem
cp *.client.key.pem /etc/pki/libvirt/private/clientkey.pem
cp *.server.key.pem /etc/pki/libvirt/private/serverkey.pem

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
