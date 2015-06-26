#!/bin/sh

# Update to ensure that the next calls will work.
apt-get update

# Dependencies for the Cloudlet Server.
apt-get install qemu-kvm libvirt-bin nmap python2.7 python-dev python-libvirt mongodb nmap libbluetooth-dev build-essential libssl-dev libffi-dev

# Dependencies for the Discovery Server.
apt-get install libnss-mdns avahi-daemon
