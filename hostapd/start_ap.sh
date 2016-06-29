#!/usr/bin/env bash

# Disable Network Manager use of Wifi and create wlan0 interface
nmcli nm wifi off
rfkill unblock wlan
sudo ifconfig wlan0 up 192.168.2.1 netmask 255.255.255.0

# Stop the dnsmasq instance used by libtirtd.
sudo killall dnsmasq
sudo stop libvirt-bin
sudo service bind9 stop

# Start dnsmasq to act as DHCP server
#sudo dnsmasq -z --dhcp-authoritative --interface=wlan0 --dhcp-range=192.168.2.20,192.168.2.100,255.255.255.0,4h

# Start hostapd
sudo hostapd -B ./hostapd-nic.conf
