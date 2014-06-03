#!/bin/sh

# Install virtualenv.
apt-get install python-pip
pip install virtualenv

# Create a virtual env to work on.
virtualenv --no-site-packages ./env

# Copy libvirt python packages to the env (there is no way to install them directly through pip).
apt-get install python-libvirt
cp /usr/lib/python2.7/dist-packages/*libvirt* ./env/lib/python2.7/site-packages/