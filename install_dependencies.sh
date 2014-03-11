#!/bin/sh

# Update to ensure that the next calls will work.
apt-get update

# Dependencies for the Cloudlet Server.
apt-get install qemu-kvm libvirt-bin gvncviewer python2.7 python-dev python-pip python-libvirt
pip install pymongo paramiko
pip install Pylons==0.9.7
pip install Routes==1.11
pip install webob==1.08
pip install WebTest==1.4.3

# Dependencies for the Discovery Server.
apt-get install libnss-mdns avahi-daemon
