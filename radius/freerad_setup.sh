#!/bin/sh

CLOUDLET_USER=$1

# Give group freeradius write permissions to the main FreeRADIUS folder so that pycloud can modify configurations.
sudo chown -R freerad:freerad /etc/freeradius/
sudo chmod -R g+rw /etc/freeradius/

# Add the user.
sudo adduser $CLOUDLET_USER freerad
