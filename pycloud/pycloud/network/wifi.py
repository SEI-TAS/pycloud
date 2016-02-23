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

###################################################################################################################
# Helper to call nmcli commands.
###################################################################################################################
def nmcli(cmd):
    return subprocess.Popen('nmcli ' + cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()

def save_network():
    pass

###################################################################################################################
# Wifi manager class.
###################################################################################################################
class WifiManager(object):
    interface = None

    ################################################################################################################
    # Return a list of SSIDs currently in range.
    # TODO: needs refreshing? how up-to-date is this info?
    ################################################################################################################
    def list_networks(self):
        # Will return a list of newline separated SSIDs.
        response = nmcli('device wifi list')
        print response

        lines = response.splitlines()
        ssids = []
        for line in lines:
            parts = line.split("'")
            if len(parts) > 1:
                ssid = parts[1]
                ssids.append(ssid)
        print ssids

        return ssids

    ################################################################################################################
    # Return the current network SSID we are connected to using our configured interface, if any, or None.
    ################################################################################################################
    def current_network(self):
        network = None
        response = nmcli('connection status | grep {}'.format(self.interface))

        for line in response.splitlines():
            if len(line) > 0:
                network = line.split()[0]
                break

        return network

    ################################################################################################################
    # Connect to a stored network.
    ################################################################################################################
    def connect_to_network(self, connection_id):
        response = nmcli('connection up id {}'.format(connection_id))

        # TODO: process result?
        return True
