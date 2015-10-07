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

# Set up Feerad permissions.
sudo freerad_setup.sh

# Setup USB permissions.
cd ../libusb
bash setup.sh

# Adds the current user to the appropriate group to get correct permissions.
# NOTE: this is done manually in a production set up, as it has to be done to the user that will be running
# system, not the current user.
sudo adduser $USER kvm
sudo adduser $USER libvirtd
sudo adduser $USER freerad
sudo adduser $USER plugdev
