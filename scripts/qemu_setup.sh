#!/bin/sh

CLOUDLET_USER=$1

# Update libvirtd's qemu config so that it will run under the proper user when started as at system level.
echo 'Setting libvirtd user, group and file ownership for qemu.'

# Uncomment these params, if commented.
sudo sed -i -e 's:^#user:user:' /etc/libvirt/qemu.conf
sudo sed -i -e 's:^#group:group:' /etc/libvirt/qemu.conf
sudo sed -i -e 's:^#dynamic_ownership:dynamic_ownership:' /etc/libvirt/qemu.conf

# Set the user to root.
sudo sed -i -e 's:^user.*$:user = "root":' /etc/libvirt/qemu.conf
sudo sed -i -e 's:^group.*$:group = "root":' /etc/libvirt/qemu.conf
sudo sed -i -e 's:^dynamic_ownership.*$:dynamic_ownership = 1:' /etc/libvirt/qemu.conf

# Restart libvirtd, if it was running, to ensure it uses these settings.
sudo service libvirt-bin stop
sudo service libvirt-bin start

# Add the user to the appropriate groups.
sudo adduser ${CLOUDLET_USER} kvm
sudo adduser ${CLOUDLET_USER} libvirtd

echo 'Qemu setup done.'
