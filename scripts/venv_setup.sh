#!/bin/sh

# Install virtualenv.
sudo -H pip install virtualenv

# Create a virtual env to work on.
virtualenv --no-site-packages ../env
