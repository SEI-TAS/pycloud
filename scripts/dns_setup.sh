#!/bin/sh

# Stop bind, in case it has any journals pending.
echo 'Stopping bind, removing journals.'
sudo service bind9 stop
sudo rm -f /var/lib/bind/db.svm.cloudlet.local.jnl

echo 'Copying templates.'

# Copy zone file template.
sudo cp ../dns/db.svm.cloudlet.local /var/lib/bind/

# NOTE: setting the cloudlet's IP will have to be done on the zone file manually.
#CLOUDLET_PUBLIC_IP=192.168.1.12
# Set IP in zone file.
#echo 'Setting IP in zone file.'
#sudo sed -i -e "s:CLOUDLET_PUBLIC_IP:$CLOUDLET_PUBLIC_IP:g" /var/lib/bind/db.svm.cloudlet.local

# Create a backup of the zone file.
sudo cp /var/lib/bind/db.svm.cloudlet.local /var/lib/bind/db.svm.cloudlet.local.backup

# Copy config file template.
sudo cp ../dns/named.conf.local /etc/bind/

# Generate and load TSIG key.
echo 'Generating TSIG key.'
dnssec-keygen -a HMAC-MD5 -b 512 -n HOST -r /dev/urandom  svm.cloudlet.local
mv Ksvm.cloudlet.local*.private Ksvm.cloudlet.local.private
TSIG_PASSWORD=`python ../pycloud/pycloud/network/tsig.py ./Ksvm.cloudlet.local.private`

# NOTE: The TSIG key will have to be copied manually to data folder in the installer case.... somehow.
mkdir ../data/dns
mv ./Ksvm.cloudlet.local.private ../data/dns/

# Remove extra key file.
sudo rm -f ./Ksvm.cloudlet.local.*

# Update the config with the newly created TSIG key.
echo 'Setting TSIG key in config file.'
sudo sed -i -e "s:TSIG_PASSWORD:$TSIG_PASSWORD:g" /etc/bind/named.conf.local

# Disable dnsmasq in NetworkManager and restart NetworkManager.
echo 'Disabling dnsmasq.'
sudo sed -i -e "s:dns=dnsmasq:#dns=dnsmasq:g" /etc/NetworkManager/NetworkManager.conf
sudo service network-manager restart

# Restart bind.
echo 'Restarting bind.'
sudo service bind9 start
