#!/bin/sh

# Update to ensure that the next calls will work.
apt-get update

# Basic Python deps.
apt-get -y install python2.7 python-dev

# Get all dependencies from the debian installer control file.
depsfile="../debian/control"
getdep=false
deparray=()
while read -r line
do
    # We are assuming the first non-python dep is qemu-kvm. If this changes, it should be changed here.
    dep=${line%","}
    if [[ "$getdep" = false && "$dep" == "qemu-kvm" ]]; then
        getdep=true
    fi

    # We are assuming the Description line is right after the last dep.
    if [[ "$getdep" = true && "$dep" == Description* ]]; then
        getdep=false
    fi

    # Add all deps to an array.
    if [[ "$getdep" = true ]]; then
        echo "***Found dependency: $dep"
        deparray=("${deparray[@]}" "$dep")
    fi
done < "$depsfile"

# Install all deps in the array.
for curr_dep in "${deparray[@]}"
do
    echo "***Installing: $curr_dep"
    apt-get -y install "$curr_dep"
done
