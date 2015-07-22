#!/bin/sh

# Update to ensure that the next calls will work.
apt-get update

# Dependencies for the Cloudlet Server.
apt-get install qemu-kvm libvirt-bin nmap python2.7 python-dev python-libvirt mongodb
apt-get install libusb-1.0.0-dev libbluetooth-dev build-essential swig libssl-dev libffi-dev

# Dependencies for the Discovery Server.
apt-get install libnss-mdns avahi-daemon
