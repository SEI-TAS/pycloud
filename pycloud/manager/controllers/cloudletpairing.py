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
__author__ = 'Keegan'

import logging
import time
import random
import os
import string


from pylons import request, response, session, tmpl_context as c
from pylons import app_globals

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.manager.lib.pages import CloudletPairingPage
from pycloud.manager.lib.pages import CloudletDiscoveryPage
from pycloud.pycloud.ska.wifi_ska_device import WiFiSKADevice
from pycloud.pycloud.pylons.lib import helpers as h

from pycloud.pycloud.model.deployment import Deployment

from pycloud.pycloud.utils import ajaxutils

import subprocess

log = logging.getLogger(__name__)

################################################################################################################
# Controller for the Pairing page.
################################################################################################################
class CloudletPairingController(BaseController):

    ############################################################################################################
    # Entry point.
    ############################################################################################################
    def GET_index(self):
        return self.GET_pair()

    ############################################################################################################
    # Displays the connection to cloudlet page
    ############################################################################################################
    def GET_pair(self):
        page = CloudletPairingPage()

        # TODO: Generate secret to display
        temp = string.join(random.sample(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", 1, 2, 3, 4, 5, 6, 7, 8, 9, 0], 6))
        page.secret = temp #secret should be alphanumeric and 6 symbols long

        return page.render()

    ############################################################################################################
    # Does the work after data is entered
    ############################################################################################################
    def POST_pair(self):

        # Generate secret to display
        secret = request.params.get('secret', None)
        ssid = request.params.get('ssid', None)
        psk = request.params.get('psk', None)
        command = "wpa_passphrase " + ssid + " " + psk + ">hostapd/wpa.conf"
        cmd = subprocess.Popen(command, shell=True, stdout=None)
        command = "wpa_supplicant -Dwext -iwlan0 -chostapd/wpa.conf"
        cmd = subprocess.Popen(command, shell=True, stdout=None)
        connection = request.params.get('connection', None)
        if connection is None:
            connection = 'wifi'

        try:
            # Create a device depending on the type.
            if connection == 'wifi':
                #port = request.params.get('port', None)
                #name = request.params.get('name', None)
                id = "10.10.10.10"
                port = "1723"
                name = "WiFi1"
                curr_device = WiFiSKADevice({'host': id, 'port': int(port), 'name': name})
                curr_device.listen()
            else:
                pass
        except Exception, e:
            print str(e)

        time.sleep(5) # For testing purposes

        return h.redirect_to(controller='devices', action='list')

    ############################################################################################################
    # Displays the discover page for cloudlet pairing.
    ############################################################################################################
    def GET_discover(self):
        page = CloudletDiscoveryPage()

        # TODO: Generate ssid and random psk here
        temp = string.join(random.sample(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", 1, 2, 3, 4, 5, 6, 7, 8, 9, 0], 6))
        host = os.uname()[1]
        page.ssid = host + "-" + temp #ssid should be "<cloudlet machine name>-<alphanumeric and 6 symbols long>"
        psk = string.join(random.sample(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", 1, 2, 3, 4, 5, 6, 7, 8, 9, 0], 6))
        page.psk = psk #psk should be alphanumeric and 6 symbols long
        command = "sed -ie \"s/xxxxxx/" + page.ssid + "/g\" hostapd/hostapd-nic.conf"
        cmd = subprocess.Popen(command, shell=True, stdout=None)
        command = "sed -ie \"s/yyyyyy/" + page.psk + "/g\" hostapd/hostapd-nic.conf"
        cmd = subprocess.Popen(command, shell=True, stdout=None)

        return page.render()

    ############################################################################################################
    # Does the wrk after data is entered
    ############################################################################################################
    def POST_discover(self):

        # Generate secret to display
        secret = request.params.get('secret', None)
        ssid = request.params.get('ssid', None)
        psk = request.params.get('psk', None)
        connection = request.params.get('connection', None)
        if connection is None:
            connection = 'wifi'

        try:
            # Create a device depending on the type.
            curr_device = None
            if connection == 'wifi':
                #port = request.params.get('port', None)
                #name = request.params.get('name', None)
                id = "10.10.10.1"
                port = "1723"
                name = "WiFi1"
                curr_device = WiFiSKADevice({'host': id, 'port': int(port), 'name': name})
            else:
                pass

            deployment = Deployment.get_instance()
            deployment.pair_cloudlet(curr_device)
        except Exception, e:
            return ajaxutils.show_and_return_error_dict(e.message)

        time.sleep(5) # For testing purposes

        return h.redirect_to(controller='devices', action='list')

