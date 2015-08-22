#!/bin/sh
# This should be run from inside the scripts folder.

# 1. System setup.

# Install debian dependencies.
sudo bash install_deb_packages.sh

# Setup pip
sudo bash pip_setup.sh

# 2. Local environment and local folder setup.

# Setup the virtual environment.
bash venv_setup.sh

# Setup the pip packages in the environment.
bash install_pip_packages.sh

# Create the egg files.
bash egg_setup.sh

# Setup Avahi Discovery Service.
sudo bash avahi_setup.sh

# Add user to the kvm group to get correct permissions.
sudo usermod -a -G kvm $USER
sudo usermod -a -G libvirtd $USER
