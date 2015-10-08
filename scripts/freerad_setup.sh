#!/usr/bin/env bash

# Give group freeradius write permissions to the main FreeRADIUS folder so that pycloud can modify configurations.
chown -R freerad:freerad /etc/freeradius/
chmod -R g+rw /etc/freeradius/
