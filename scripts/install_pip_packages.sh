#!/bin/sh
source ../env/bin/activate
pip install -r ../requirements.txt

# python-adb is not in the PyPi package repo, it has to be installed separately.
bash python-adb_setup.sh
