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
import random
import os


from pylons import request, response, session, tmpl_context as c
from pylons import app_globals

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.manager.lib.pages import CloudletPairingPage
from pycloud.manager.lib.pages import CloudletDiscoveryPage
from pycloud.pycloud.ska.wifi_ska_device import WiFiSKADevice
from pycloud.pycloud.cloudlet import Cloudlet, get_cloudlet_instance
from pycloud.pycloud.pylons.lib import helpers as h

from pycloud.pycloud.model.deployment import Deployment

from pycloud.pycloud.utils import ajaxutils

from pycloud.pycloud.network import wifi_adhoc

import subprocess

log = logging.getLogger(__name__)

SKA_CLIENT_IP = '10.10.10.1'
SKA_SERVER_IP = '10.10.10.10'
SKA_SERVER_PORT = '1723'


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
        temp = ''.join(random.sample(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"], 6))
        page.secret = temp #secret should be alphanumeric and 6 symbols long

        return page.render()

    ############################################################################################################
    # Does the work after data is entered
    ############################################################################################################
    def POST_discover(self):
        client_cloudlet = None
        try:
            secret = request.params.get('secret', None)

            # Enable ad-hoc mode.
            wifi_adhoc.enable_adhoc_mode(SKA_SERVER_IP)

            # Here we are abusing the WiFiSKADevice object which, in this case, we don't have information of since we
            # will be waiting for messages from it.
            client_cloudlet_name = "WiFiClient"
            cloudlet = get_cloudlet_instance()
            client_cloudlet = WiFiSKADevice({'host': SKA_CLIENT_IP, 'port': 0, 'name': client_cloudlet_name, 'secret': secret})
            client_cloudlet.wait_for_messages(host=SKA_SERVER_IP, port=SKA_SERVER_PORT, secret=secret, files_path=cloudlet.cloudletCredentialsFolder)
        except Exception, e:
            print str(e)
            raise e
        finally:
            if client_cloudlet is not None:
                try:
                    print 'Listener will shut down in 60 seconds.'
                    command = "./wpa_supplicant/stop_adhoc_mode.sh"
                    subprocess.Popen(command, shell=True, stdin=None, stdout=None, stderr=None)

                except Exception, e:
                    error = "Error launching timer function: " + str(e)
                    print error
                    raise Exception(error)

        return h.redirect_to(controller='devices', action='list')

    ############################################################################################################
    # Displays the discover page for cloudlet pairing.
    ############################################################################################################
    def GET_discover(self):
        page = CloudletDiscoveryPage()

        # Generate ssid and random psk here
        temp = ''.join(random.sample(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"], 6))
        host = os.uname()[1]
        page.ssid = host + "-" + temp #ssid should be "<cloudlet machine name>-<alphanumeric and 6 symbols long>"
        psk = ''.join(random.sample(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"], 8))
        page.psk = psk #psk should be alphanumeric and 8 symbols long

        wifi_adhoc.configure_wpa2_params(page.ssid, page.psk)

        return page.render()

    ############################################################################################################
    # Does the wrk after data is entered
    ############################################################################################################
    def POST_pair(self):
        # Generate secret to display
        device_type = 'cloudlet'
        secret = request.params.get('secret', None)
        ssid = request.params.get('ssid', None)
        psk = request.params.get('psk', None)

        connection = request.params.get('connection', None)
        if connection is None:
            connection = 'wifi'

        remote_cloudlet = None
        try:
            if connection == 'wifi':
                # Set up the ad-hoc network.
                wifi_adhoc.configure_wpa2_params(ssid, psk)
                wifi_adhoc.enable_adhoc_mode(SKA_CLIENT_IP)

                # Connect to the server (cloudlet) in the network.
                remote_cloudlet_name = "WiFiServer"
                remote_cloudlet = WiFiSKADevice({'host': SKA_SERVER_IP, 'port': int(SKA_SERVER_PORT),
                                                 'name': remote_cloudlet_name, 'secret': secret})
                successful_connection = remote_cloudlet.connect()
                if not successful_connection:
                    raise Exception("Could not connect to cloudlet with id {}.".format(ssid))

            # TODO: test this.
            # Get the device id.
            id_data = remote_cloudlet.get_data({'device_id': 'none'})
            device_internal_id = id_data['device_id']
            print 'Device id: ' + device_internal_id

            # Pair the device, send the credentials, and clear their local files.
            deployment = Deployment.get_instance()
            device_keys = deployment.pair_device(device_internal_id, remote_cloudlet.get_name(), device_type)
            deployment.send_paired_credentials(remote_cloudlet, device_keys)
            deployment.clear_device_keys(device_keys)

        except Exception, e:
            return ajaxutils.show_and_return_error_dict(e.message)

        finally:
            if remote_cloudlet is not None:
                try:
                    print 'Disconnecting from cloudlet.'
                    remote_cloudlet.disconnect()
                    command = "./wpa_supplicant/stop_adhoc_mode.sh"
                    subprocess.Popen(command, shell=True, stdin=None, stdout=None, stderr=None)

                except Exception, e:
                    error = "Error disconnecting" + str(e)
                    print error
                    raise Exception(error)

        return h.redirect_to(controller='devices', action='list')
