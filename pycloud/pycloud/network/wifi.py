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
import time


###################################################################################################################
# Helper to call nmcli commands.
###################################################################################################################
def nmcli(cmd):
    return subprocess.Popen('nmcli ' + cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()


###################################################################################################################
# Wifi manager class.
###################################################################################################################
class WifiManager(object):

    ################################################################################################################
    # Return a list of SSIDs currently in range.
    ################################################################################################################
    @staticmethod
    def list_networks():
        # Turn on wifi just in case, and wait for a couple of seconds it turns on.
        response = nmcli('nm wifi on')
        if response is not None and response.strip() != '':
            raise Exception(response)
        time.sleep(5)

        # Will return a list of newline separated SSIDs.
        response = nmcli('-t -f SSID device wifi list')

        lines = response.splitlines()
        ssids = []
        for line in lines:
            ssid = line.strip("'")
            ssids.append(ssid)

        return ssids

    ################################################################################################################
    # Return the current network SSID we are connected to using our configured interface, if any, or None.
    ################################################################################################################
    @staticmethod
    def current_network(interface):
        ssid = None
        response = nmcli('-t -f NAME,DEVICES connection status | grep {}'.format(interface))

        for line in response.splitlines():
            if len(line) > 0:
                ssid = line.split(':')[0]
                break

        return ssid

    ################################################################################################################
    # Connect to a stored network.
    ################################################################################################################
    @staticmethod
    def connect_to_network(connection_id):
        # NOTE: only works if called from root user or user at console.
        response = nmcli('connection up id "{}"'.format(connection_id))
        if response is not None and response.strip() != '':
            raise Exception(response)

    ################################################################################################################
    # Connect to a stored network.
    ################################################################################################################
    @staticmethod
    def disconnect_from_network():
        # NOTE: only works if called from root user or user at console.
        response = nmcli('nm wifi off')

        if response is not None and response.strip() != '':
            raise Exception(response)