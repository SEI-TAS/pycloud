#!/bin/sh
# This should be run from inside the scripts folder, without sudo.

# Assuming the user calling the script is the user pycloud will run under.
CLOUDLET_USER=${USER}

# Data folder.
DATA_FOLDER=./data

######################################################################
# 1. Scripts used only in dev setup.
######################################################################

# Install debian dependencies.
sudo bash install_deb_packages.sh

# Setup pip
sudo bash pip_setup.sh

# Setup the virtual environment.
bash venv_setup.sh

# Setup the pip packages in the environment.
bash install_pip_packages.sh

# Create the egg metadata files, needed so that Paste can actually serve pycloud apps.
bash egg_setup.sh

# Setup Avahi Discovery Service.
cd ../discovery
bash avahi_setup.sh
cd ../scripts

# Create data folder, if needed.
mkdir -p ${DATA_FOLDER}

######################################################################
# 2. Scripts common with prod setup.
######################################################################

# Setup libvirtd and qemu.
bash qemu_setup.sh ${CLOUDLET_USER}

# Set up FreeRADIUS.
cd ../radius
sudo bash freerad_setup.sh ${CLOUDLET_USER}

# Setup USB.
cd ../libusb
bash libusb_setup.sh ${CLOUDLET_USER}

# Set up DNS server.
cd ../dns
bash dns_setup.sh ../${DATA_FOLDER}

######################################################################
# 3. Other final changes for dev env only.
######################################################################

# Setup FreeRADIUS reload job.
cd ../radius/auto_reload
sudo bash freerad_auto_reload_setup.sh
cd ../../

# Back to this folder.
cd ../scripts
