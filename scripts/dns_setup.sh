#!/bin/sh

# Needs to be called with sudo.

echo 'Copying templates.'

# Copy zone file template.
sudo cp ../dns/db.svm.cloudlet.local /var/lib/bind/

# Copy config file template.
sudo cp ../dns/named.conf.local /etc/bind/

# TODO: Get the cloudlet's public IP.
CLOUDLET_PUBLIC_IP=192.168.0.112

# Set IP in zone file.
echo 'Setting IP in zone file.'
sudo sed -i -e "s:CLOUDLET_PUBLIC_IP:$CLOUDLET_PUBLIC_IP:g" /var/lib/bind/db.svm.cloudlet.local

# Generate and load TSIG key.
echo 'Generating TSIG key.'
dnssec-keygen -a HMAC-MD5 -b 512 -n HOST -r /dev/urandom  svm.cloudlet.local
mv Ksvm.cloudlet.local*.private Ksvm.cloudlet.local.private
TSIG_PASSWORD=`python ../pycloud/pycloud/network/tsig.py ./Ksvm.cloudlet.local.private`

# TODO: CopyTSIG key to data folder.
mkdir ../data/dns
mv ./Ksvm.cloudlet.local.private ../data/dns/

# Update the config with the newly created TSIG key.
echo 'Setting TSIG key in config file.'
sudo sed -i -e "s:TSIG_PASSWORD:$TSIG_PASSWORD:g" /etc/bind/named.conf.local

# Disable dnsmasq in NetworkManager and restart NetworkManager.
echo 'Disabling dnsmasq.'
sudo sed -i -e "s:dns=dnsmasq:#dns=dnsmasq:g" /etc/NetworkManager/NetworkManager.conf
sudo service network-manager restart

# Restart bind.
echo 'Restarting bind.'
sudo service bind9 restart
