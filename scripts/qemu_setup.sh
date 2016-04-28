#!/bin/sh

# Assuming the user calling the script is the user pycloud will run under.
CLOUDLET_USER=$USER

# Update libvirtd's qemu config so that it will run under the proper user when started as at system level.
echo 'Setting libvirtd user, group and file ownership for qemu.'
sudo sed -i -e "s:#user = \"root\":user = \"$CLOUDLET_USER\":g" /etc/libvirt/qemu.conf
sudo sed -i -e "s:#group = \"root\":group = \"$CLOUDLET_USER\":g" /etc/libvirt/qemu.conf
sudo sed -i -e "s:#dynamic_ownership = 1:dynamic_ownership = 0:g" /etc/libvirt/qemu.conf

# Restart libvirtd, if it was running, to ensure it uses these settings.
sudo stop libvirt-bin
sudo start libvirt-bin
