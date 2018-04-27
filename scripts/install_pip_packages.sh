#!/bin/sh
source ../env/bin/activate
pip install -r ../requirements.txt

# Copy libvirt python packages to the env (there is a high likelyhood of compatibility issues if installed via pip).
cp /usr/lib/python2.7/dist-packages/*libvirt* ../env/lib/python2.7/site-packages/
