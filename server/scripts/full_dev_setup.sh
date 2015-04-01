#!/bin/sh

# Install debian dependencies.
sudo bash install_deb_packages.sh

# Setup the virtual environment.
sudo bash venv_setup.sh

# Setup the pip packages in the environment.
bash install_pip_packages.sh

# Create the egg files.
cd ..
python setup.py egg_info
cd ./scripts