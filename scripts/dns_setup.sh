#!/bin/sh

# Needs to be called with sudo.

# Copy zone file template.
cp ../dns/db.svm.cloudlet.local /var/lib/bind/

# Copy config file template.
cp ../dns/named.conf.local /etc/bind/

# TODO: Get the cloudlet's public IP.
CLOUDLET_PUBLIC_IP=192.168.0.112

# Set IP in zone file.
sed -i -e "s:CLOUDLET_PUBLIC_IP:$CLOUDLET_PUBLIC_IP:g" /var/lib/bind/db.svm.cloudlet.local

# Generate and load TSIG key.
dnssec-keygen -a HMAC-MD5 -b 512 -n USER svm.cloudlet.local
mv Ksvm.cloudlet.local*.private Ksvm.cloudlet.local.private
TSIG_PASSWORD=`python ../pycloud/pycloud/network/cloudlet_dns.py ./Ksvm.cloudlet.local.private`

# TODO: CopyTSIG key to data folder.
mkdir ../data/dns
mv ./Ksvm.cloudlet.local.private ../data/dns/

# Update the config with the newly created TSIG key.
sed -i -e "s:TSIG_PASSWORD:$TSIG_PASSWORD:g" /etc/bind/named.conf.local

# Disable dnsmasq in NetworkManager and restart NetworkManager.
sed -i -e "s:dns=dnsmasq:#dns=dnsmasq:g" /etc/NetworkManager/NetworkManager.conf
service network-manager restart

# Restart bind.
service bind9 restart
