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

from pylons import request, response, session, tmpl_context as c
from pylons import app_globals

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.manager.lib.pages import PairingPage
from pycloud.pycloud.ska.bluetooth_ska_device import BluetoothSKADevice
from pycloud.pycloud.ska.adb_ska_device import ADBSKADevice
from pycloud.pycloud.pylons.lib import helpers as h

from pycloud.pycloud.model.deployment import Deployment

from pycloud.pycloud.pylons.lib.util import asjson
from pycloud.pycloud.utils import ajaxutils

log = logging.getLogger(__name__)

################################################################################################################
# Controller for the Pairing page.
################################################################################################################
class PairingController(BaseController):

    ############################################################################################################
    # Entry point.
    ############################################################################################################
    def GET_index(self):
        return self.GET_available()

    ############################################################################################################
    # Lists the connected devices, and lets the system pair to one of them.
    ############################################################################################################
    def GET_available(self):
        page = PairingPage()
        page.devices = []
        page.bt_selected = ''
        page.usb_selected = ''

        # Ensure the device types are initialized.
        BluetoothSKADevice.initialize(app_globals.cloudlet.data_folder)
        ADBSKADevice.initialize(app_globals.cloudlet.data_folder)

        page.connection = request.params.get('connection', None)
        if page.connection is None:
            page.connection = 'usb'

        try:
            if page.connection == 'bt':
                page.bt_selected = 'selected'
                page.devices = BluetoothSKADevice.list_devices()
            else:
                page.usb_selected = 'selected'
                page.devices = ADBSKADevice.list_devices()
        except Exception, e:
            print e
            h.flash('Error looking for devices: ' + str(e))

        return page.render()

    ############################################################################################################
    # Pairs with a device.
    ############################################################################################################
    @asjson
    def GET_pair(self, id):
        device_type = 'mobile'

        connection = request.params.get('connection', None)
        if connection is None:
            connection = 'bt'

        curr_device = None
        try:
            # Create a device depending on the type.
            if connection == 'bt':
                port = request.params.get('port', None)
                name = request.params.get('name', None)
                curr_device = BluetoothSKADevice({'host': id, 'port': int(port), 'name': name})
            else:
                curr_device = ADBSKADevice(id)

            # Now the pairing process will be followed, generating all required credentials.
            # The first step is to connect to the device.
            successful_connection = curr_device.connect()
            if not successful_connection:
                raise Exception("Could not connect to device with id {}.".format(id))

            # Get the device id.
            id_data = curr_device.get_data({'device_id': 'none'})
            device_internal_id = id_data['device_id']
            print 'Device id: ' + device_internal_id

            # Pair the device, send the credentials, and clear their local files.
            deployment = Deployment.get_instance()
            device_keys = deployment.pair_device(device_internal_id, curr_device.get_name(), device_type)
            deployment.send_paired_credentials(curr_device, device_keys)
            deployment.clear_device_keys(device_keys)
        except Exception, e:
            return ajaxutils.show_and_return_error_dict(e.message)
        finally:
            if curr_device is not None:
                try:
                    print 'Closing connection.'
                    curr_device.disconnect()
                except Exception, e:
                    error = "Error closing connection with device: " + str(e)
                    return ajaxutils.show_and_return_error_dict(error)

        return ajaxutils.JSON_OK
