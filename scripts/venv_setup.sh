#!/bin/sh

# Install virtualenv.
pip install virtualenv

# Create a virtual env to work on.
virtualenv ../env #--no-site-packages

# Copy libvirt python packages to the env (there is no way to install them directly through pip).
cp /usr/lib/python2.7/dist-packages/*libvirt* ../env/lib/python2.7/site-packages/