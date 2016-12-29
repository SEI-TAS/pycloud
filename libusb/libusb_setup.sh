#!/bin/sh

CLOUDLET_USER=$1

# Add rule to allow connection to most common Android phone vendors.
sudo cp 95-android.rules /etc/udev/rules.d/
sudo chmod a+r /etc/udev/rules.d/95-android.rules

# Reload usb services.
sudo udevadm control --reload-rules
sudo service udev restart
sudo udevadm trigger

# Add to group.
sudo adduser $CLOUDLET_USER plugdev
