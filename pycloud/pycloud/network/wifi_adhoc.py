# KVM-based Discoverable Cloudlet (KD-Cloudlet)
# Copyright (c) 2015 Carnegie Mellon University.
# All Rights Reserved.
#
# THIS SOFTWARE IS PROVIDED "AS IS," WITH NO WARRANTIES WHATSOEVER. CARNEGIE MELLON UNIVERSITY EXPRESSLY DISCLAIMS TO THE FULLEST EXTENT PERMITTEDBY LAW ALL EXPRESS, IMPLIED, AND STATUTORY WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT OF PROPRIETARY RIGHTS.
#
# Released under a modified BSD license, please see license.txt for full terms.
# DM-0002138
#
# KD-Cloudlet includes and/or makes use of the following Third-Party Software subject to their own licenses:
# MiniMongo
# Copyright (c) 2010-2014, Steve Lacy
# All rights reserved. Released under BSD license.
# https://github.com/MiniMongo/minimongo/blob/master/LICENSE
#
# Bootstrap
# Copyright (c) 2011-2015 Twitter, Inc.
# Released under the MIT License
# https://github.com/twbs/bootstrap/blob/master/LICENSE
#
# jQuery JavaScript Library v1.11.0
# http://jquery.com/
# Includes Sizzle.js
# http://sizzlejs.com/
# Copyright 2005, 2014 jQuery Foundation, Inc. and other contributors
# Released under the MIT license
# http://jquery.org/license

import subprocess

CONFIGS_FOLDER = 'wpa_supplicant'

######################################################################################################################
# Checks that there is an enabled WiFi device, and returns its name.
######################################################################################################################
def get_adapter_name():
    internal_name = None

    cmd = subprocess.Popen('iw dev', shell=True, stdout=subprocess.PIPE)
    for line in cmd.stdout:
        if "Interface" in line:
            internal_name = line.split(' ')[1]
            internal_name = internal_name.replace("\n", "")
            break

    if internal_name is not None:
        print "WiFi adapter with name {} found".format(internal_name)
    else:
        print "WiFi adapter not found."

    return internal_name


####################################################################################################################
#
####################################################################################################################
def enable_adhoc_mode(ip_address):
    # Check that there is a WiFi adapter available.
    adapter_address = get_adapter_name()
    if adapter_address is None:
        raise Exception("WiFi adapter not available.")

    # Turning off NetworkManager.
    print 'Turning off NetworkManager temporarily'
    command = "sudo stop network-manager"
    cmd = subprocess.Popen(command, shell=True, stdout=None)
    cmd.wait()

    # Remove previous adapter configuration.
    print 'Enabling wi-fi ad-hoc mode'
    command = "sudo rm /run/wpa_supplicant/" + adapter_address
    cmd = subprocess.Popen(command, shell=True, stdout=None)
    cmd.wait()

    # Start the wpa_supplicant daemon.
    command = "sudo wpa_supplicant -B -Dnl80211,wext -i" + adapter_address + " -c" + CONFIGS_FOLDER + "/wpa-nic.conf"
    cmd = subprocess.Popen(command, shell=True, stdout=None)
    cmd.wait()

    # Configure our static IP.
    command = "sudo ifconfig " + adapter_address + " inet " + ip_address + " netmask 255.255.255.0 up"
    cmd = subprocess.Popen(command, shell=True, stdout=None)
    cmd.wait()

    print 'Wi-Fi ad-hoc mode should be enabled now'

    return True


####################################################################################################################
#
####################################################################################################################
def disable_adhoc_mode():
    # Check that there is a WiFi adapter available.
    adapter_address = get_adapter_name()
    if adapter_address is None:
        raise Exception("WiFi adapter not available.")

    # Stop wpa_supplicant daemon.
    print 'Disabling wi-fi ad-hoc mode'
    command = "pkill -f 'wpa_supplicant'"
    cmd = subprocess.Popen(command, shell=True, stdout=None)
    cmd.wait()

    # Configure our static IP.
    command = "sudo ifconfig " + adapter_address + " down"
    cmd = subprocess.Popen(command, shell=True, stdout=None)
    cmd.wait()

    print 'Wi-Fi ad-hoc mode should be disabled now'

    # Turning on NetworkManager.
    print 'Turning on NetworkManager'
    command = "sudo start network-manager"
    cmd = subprocess.Popen(command, shell=True, stdout=None)
    cmd.wait()

    return True


####################################################################################################################
#
####################################################################################################################
def configure_wpa2_params(ssid, psk):
    command = "sed -e \"s/xxxx/" + ssid + "/g\" < " + CONFIGS_FOLDER + "/wpa.conf > " + CONFIGS_FOLDER + "/wpa-tmp.conf"
    print "1 " + command
    cmd = subprocess.Popen(command, shell=True, stdout=None)

    cmd.wait()
    command = "sed -e \"s/yyyy/" + psk + "/g\" < " + CONFIGS_FOLDER + "/wpa-tmp.conf > " + CONFIGS_FOLDER + "/wpa-nic.conf"
    print "2 " + command
    cmd = subprocess.Popen(command, shell=True, stdout=None)
    cmd.wait()
