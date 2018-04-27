#!/bin/sh

echo 'Setting cloudlet service in avahi.'

# Copy the discovery setup file.
sudo cp cloudlet.service /etc/avahi/services/

# Restart to ensure it finds the cloudlet service.
sudo service avahi-daemon stop
sudo service avahi-daemon start

echo 'Avahi setup done.'