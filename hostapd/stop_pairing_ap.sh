#!/usr/bin/env bash

# Give the pairing time to work, then reset WiFi
sleep 60

# Turn off the hotspot.
sudo pkill -f 'wpa_supplicant'

# Undo changes to return control to NM.
sudo ifconfig wlan1 down
#rfkill block wlan
#nmcli nm wifi on

# Restart libvirtd and its dnsmasq.
sudo killall dnsmasq
sudo start libvirt-bin
sudo service bind9 start
