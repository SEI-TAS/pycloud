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
def nmcli(cmd, response_should_be_empty=False):
    full_command = 'nmcli ' + cmd
    print 'Executing nmcli command: ' + full_command
    response = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
    print 'Response: ' + response
    if response_should_be_empty:
        if response is not None and response.strip() != '':
            raise Exception(response)

    return response


###################################################################################################################
# Wifi manager class.
###################################################################################################################
class WifiManager(object):

    CLOUDLET_NETWORK_PREFIX = 'cloudlet'

    ################################################################################################################
    #
    ################################################################################################################
    @staticmethod
    def is_wifi_enabled():
        response = nmcli('nm wifi')
        lines = response.splitlines()
        STATUS_LINE_ROW = 1
        if len(lines) > STATUS_LINE_ROW:
            status_line = lines[STATUS_LINE_ROW].strip()
            is_enabled = (status_line == 'enabled')
            return is_enabled
        else:
            raise Exception("No wifi adapter found!")

    ################################################################################################################
    # Turn on wifi, and wait for a couple of seconds it turns on.
    # NOTE: only works if called from root user or user at console, not from SSH with a regular user.
    ################################################################################################################
    @staticmethod
    def turn_wifi_on():
        nmcli('nm wifi on', response_should_be_empty=True)
        time.sleep(5)

    ################################################################################################################
    # Turn on wifi, and wait for a couple of seconds it turns on.
    # NOTE: only works if called from root user or user at console, not from SSH with a regular user.
    ################################################################################################################
    @staticmethod
    def turn_wifi_off():
        nmcli('nm wifi off', response_should_be_empty=True)

    ################################################################################################################
    # Return a list of SSIDs currently in range.
    ################################################################################################################
    @staticmethod
    def list_available_networks():
        if not WifiManager.is_wifi_enabled():
            WifiManager.turn_wifi_on()

        # Will return a list of newline separated SSIDs.
        response = nmcli('-t -f SSID device wifi list')

        lines = response.splitlines()
        ssids = []
        for line in lines:
            ssid = line.strip("'")
            if ssid.startswith(WifiManager.CLOUDLET_NETWORK_PREFIX):
                ssids.append(ssid)

        return ssids

    ################################################################################################################
    # Return a list of stored network profiles.
    ################################################################################################################
    @staticmethod
    def list_known_networks():
        # Spaces may make it hard to get the profile name, unless we filter only the name.
        # However, by getting only the name we will also get non wifi profiles, so we will do a cross-match between
        # these two lists.
        all_networks = nmcli('-t -f NAME con list')
        wifi_networks = nmcli('con list | grep 802-11-wireless')

        all_network_lines = all_networks.splitlines()
        wifi_networks_lines = wifi_networks.splitlines()
        wifi_network_list = []
        for line in all_network_lines:
            network_name = line.strip("'")

            # Check that this network name is in the list of wifi networks.
            for wifi_line in wifi_networks_lines:
                if wifi_line.startswith(network_name):
                    if network_name.startswith(WifiManager.CLOUDLET_NETWORK_PREFIX):
                        wifi_network_list.append(network_name)
                        break

        return wifi_network_list

    ################################################################################################################
    # Returns a list of known networks that are currently available.
    ################################################################################################################
    @staticmethod
    def list_available_known_networks():
        available_known_networks = []
        known_networks = WifiManager.list_known_networks()
        available_networks = WifiManager.list_available_networks()
        for network in known_networks:
            if network in available_networks:
                available_known_networks.append(network)

        return available_known_networks

    ################################################################################################################
    # Return the current network SSID we are connected to using our configured interface, if any, or None.
    ################################################################################################################
    @staticmethod
    def get_current_network(interface):
        ssid = None
        response = nmcli('-t -f NAME,DEVICE connection show --active | grep {}'.format(interface))

        for line in response.splitlines():
            if len(line) > 0:
                ssid = line.split(':')[0]
                if ssid == '** (process':
                    # This means there was an error getting the current network, most likely because wifi is off.
                    ssid = 'disconnected'
                break

        return ssid

    ################################################################################################################
    #
    ################################################################################################################
    @staticmethod
    def is_connected_to_cloudlet_network(interface):
        is_connected_to_cloudlet_net = False
        current_network = WifiManager.get_current_network(interface)
        if current_network is not None:
            is_connected_to_cloudlet_net = current_network.startswith(WifiManager.CLOUDLET_NETWORK_PREFIX)
        return is_connected_to_cloudlet_net

    ################################################################################################################
    # Connect to a stored network.
    # NOTE: only works if called from root user or user at console, not from SSH with a regular user.
    ################################################################################################################
    @staticmethod
    def connect_to_network(connection_id):
        if not WifiManager.is_wifi_enabled():
            WifiManager.turn_wifi_on()

        nmcli('connection up id "{}"'.format(connection_id), response_should_be_empty=True)

    ################################################################################################################
    # Disconnect from current wifi network, only way to force it not to reconnect is to disable wifi.
    ################################################################################################################
    @staticmethod
    def disconnect_from_network(interface):
        if WifiManager.is_wifi_enabled():
            current_network = WifiManager.get_current_network(interface)
            if current_network is not None:
                nmcli('connection down id "{}"'.format(current_network), response_should_be_empty=True)
