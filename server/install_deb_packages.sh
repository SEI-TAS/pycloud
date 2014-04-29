#!/bin/sh

# Update to ensure that the next calls will work.
apt-get update

# Dependencies for the Cloudlet Server.
apt-get install qemu-kvm libvirt-bin gvncviewer python2.7 python-dev python-pip python-libvirt mongodb

# Dependencies for the Discovery Server.
apt-get install libnss-mdns avahi-daemon
