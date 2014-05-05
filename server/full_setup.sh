#!/bin/sh

# Install debian dependencies.
sudo bash install_deb_packages.sh

# Get the git repo.
git clone ssh://git@go.tm.rtsslab/ams/pycloud

# Setup the virtual environment.
sudo bash venv_setup.sh

# Setup the pip packages in the environment.
source ./env/bin/activate
bash install_pip_packages.sh

# Create the egg files.
bash create_eggs.sh