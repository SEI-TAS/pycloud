#! /bin/sh
cd /etc/freeradius

# Reload server if certs changed.
restarting=false
if [[ ! -e .last-reload ]]  || [[ "eap.conf" -nt ".last-reload" ]]; then
    echo "Restarting Freeradius..."
    service freeradius restart
    restarting=true
fi

# Reload configs if there is no .last-reload file, or if the users file has changed since we last checked.
if [[ "$restarting" = false ]]; then
    if [[ ! -e .last-reload ]] || [[ "users" -nt ".last-reload" ]]; then
        echo "Reloading Freeradius configs..."
        service freeradius reload
    fi
fi

# Update the modification time for the timestamp file, creating it if it didn't exist.
touch .last-reload
