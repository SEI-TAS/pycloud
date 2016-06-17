#!/bin/sh

DATA_FOLDER=$1

# Stop bind, in case it has any journals pending.
echo 'Stopping bind, removing journals.'
sudo service bind9 stop
sudo rm -f /var/lib/bind/db.svm.cloudlet.local.jnl

echo 'Copying templates.'

# Copy zone file template, and create a backup, just in case, since it will be dynamically modified by bind.
# NOTE: setting the cloudlet's IP will have to be done on the zone file manually.
sudo cp db.svm.cloudlet.local /var/lib/bind/
sudo cp /var/lib/bind/db.svm.cloudlet.local /var/lib/bind/db.svm.cloudlet.local.backup

# Copy config file template.
sudo cp named.conf.local /etc/bind/

# Generate TSIG key file with default name scheme.
echo 'Generating TSIG key.'
dnssec-keygen -a HMAC-MD5 -b 512 -n HOST -r /dev/urandom  svm.cloudlet.local

# Move keyfile to proper folder and name.
# NOTE: The TSIG key will have to be copied manually to data folder in the installer case.... somehow.
TSIG_PASSWORD_FOLDER=${DATA_FOLDER}/dns
TSIG_PASSWORD_FILE=Ksvm.cloudlet.local.private
mv Ksvm.cloudlet.local*.private ${TSIG_PASSWORD_FILE}
mkdir -p ${TSIG_PASSWORD_FOLDER}
mv ./${TSIG_PASSWORD_FILE} ${TSIG_PASSWORD_FOLDER}/

# Remove extra key files, if any.
sudo rm -f ./Ksvm.cloudlet.local.*

# Update the config with the newly created TSIG key.
TSIG_PASSWORD_CONTENTS=`python ../pycloud/pycloud/network/tsig.py ./${TSIG_PASSWORD_FOLDER}/${TSIG_PASSWORD_FILE}`
echo 'Setting TSIG key in config file.'
sudo sed -i -e "s:TSIG_PASSWORD:${TSIG_PASSWORD_CONTENTS}:g" /etc/bind/named.conf.local

# Disable dnsmasq in NetworkManager and restart NetworkManager (to avoid DNS conflicts with it).
echo 'Disabling dnsmasq.'
sudo sed -i -e "s:^dns=dnsmasq:#dns=dnsmasq:g" /etc/NetworkManager/NetworkManager.conf
sudo service network-manager restart

# Restart bind.
echo 'Restarting bind.'
sudo service bind9 start
