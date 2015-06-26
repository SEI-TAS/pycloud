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
__author__ = 'Sebastian'

import logging

from pylons import request, response, session, tmpl_context as c, url

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.manager.lib.pages import SKADevicesPage
from pycloud.pycloud.ska.bluetooth_ska_device import BluetoothSKADevice
from pycloud.pycloud.ska.adb_ska_device import ADBSKADevice
from pycloud.pycloud.ibc import ibc
import pycloud.pycloud.utils.pki

from pycloud.pycloud.pylons.lib.util import asjson
from pycloud.pycloud.utils import ajaxutils

log = logging.getLogger(__name__)

################################################################################################################
# Controller for the Services page.
################################################################################################################
class SKAController(BaseController):

    ############################################################################################################
    # Entry point.
    ############################################################################################################
    def GET_index(self):
        return self.GET_devices()

    ############################################################################################################
    # Lists the connected devices, and lets the system pair to one of them.
    ############################################################################################################
    def GET_devices(self):
        page = SKADevicesPage()
        page.devices = []
        page.bt_selected = ''
        page.usb_selected = ''

        page.connection = request.params.get('connection', None)
        if page.connection is None:
            page.connection = 'usb'

        if page.connection == 'bt':
            try:
                page.bt_selected = 'selected'
                page.devices = BluetoothSKADevice.list_devices()
            except Exception, e:
                print e
                pass
                # Should show a warning to user.
        else:
            try:
                page.usb_selected = 'selected'
                page.devices = ADBSKADevice.list_devices()
            except Exception, e:
                print e
                pass
                # Should show a warning to user.

        return page.render()

    ############################################################################################################
    # Pairs with a device.
    ############################################################################################################
    @asjson
    def GET_pair(self, id):
        connection = request.params.get('connection', None)
        if connection is None:
            connection = 'bt'

        # Get a list of devices depending on the connection type.
        if connection == 'bt':
            devices = BluetoothSKADevice.list_devices()
        else:
            devices = ADBSKADevice.list_devices()

        # Find if the device we want to connect to is still there.
        curr_device = None
        for device in devices:
            if device.get_name() == id:
                curr_device = device
                break

        if curr_device is None:
            raise Exception("Device with id {} not found for pairing.".format(id))

        # Here the whole pairing process should be followed, generating IBC keys and all.
        # For now, we are just getting the id, and sending a test file.
        if curr_device.connect():
            device_internal_id = curr_device.get_id()
            print device_internal_id

            # password = curr_device.get_password()

            #ibc_private_key = ibc.generate_private_key(device_internal_id, password)
            #certificate = ibc.generate_client_certificate(device_internal_id, ibc_private_key)

            #curr_device.send_files([ibc_private_key, certificate.cert, certificate.private_key])

            curr_device.send_server_public_key('/home/adminuser/test.txt')
            curr_device.send_device_private_key('/home/adminuser/test.txt')
            curr_device.send_server_certificate('/home/adminuser/test.txt')
            curr_device.send_device_certificate('/home/adminuser/test.txt')

            # TODO: get ssid from config file
            curr_device.send_network_id('test_ssid')

            curr_device.disconnect()

        return ajaxutils.JSON_OK
