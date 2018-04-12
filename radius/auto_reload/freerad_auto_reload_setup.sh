#!/usr/bin/env bash

# NOTE: This script should be called with root permissions.

SCRIPTS_PATH=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# Copy fixed Upstart job that will allow reload to work.
cp freeradius.conf /etc/init

# Create cron job that will call our scripts to constantly check for changes in the config and to reload FreeRADIUS when
# this happens
cp freerad.dev /etc/cron.d/freerad

# Update the cron job so that it has the appropriate paths.
sed -i -e "s:pycloud_scripts_path:$SCRIPTS_PATH:g" /etc/cron.d/freerad

echo "Finished setting up cron job"
