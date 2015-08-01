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
import os

from pylons import request, response, session, tmpl_context as c
from pylons import app_globals

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.manager.lib.pages import PairingPage
from pycloud.pycloud.ska.bluetooth_ska_device import BluetoothSKADevice
from pycloud.pycloud.ska.adb_ska_device import ADBSKADevice
from pycloud.pycloud.pylons.lib import helpers as h

from pycloud.pycloud.model.paired_device import PairedDevice
from pycloud.pycloud.ibc import radius
from pycloud.pycloud.ibc import credentials

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
        if curr_device.connect():
            id_data = curr_device.get_data({'device_id': 'none'})
            print id_data
            device_internal_id = id_data['device_id']

            # Check if the device was already paired, and if so, abort.
            previously_paired_device = PairedDevice.by_id(device_internal_id)
            if previously_paired_device:
                return ajaxutils.show_and_return_error_dict("Device with id " + device_internal_id + " is already paired.")

            # Create device private key and get the password from hash.
            server_private_key_path = os.path.join(app_globals.cloudlet.data_folder, 'credentials/server_private_key')
            client_private_key_path = os.path.join(app_globals.cloudlet.data_folder, 'credentials/temp_device_key')
            device_keys = credentials.DeviceCredentials("SKE", [server_private_key_path, device_internal_id])
            device_keys.insert_into_radius()
            device_keys.save_to_file([client_private_key_path])
            password = device_keys.device_hash

            # Send the device's private key.
            curr_device.send_file(client_private_key_path, 'device.key')

            # Send certificate.
            cert_path = radius.get_radius_cert_path()
            cert_file_name = radius.RADIUS_CERT_FILE_NAME
            curr_device.send_file(cert_path, cert_file_name)

            # Send data needed to finish configuration in device.
            ssid = app_globals.cloudlet.ssid
            curr_device.send_data({'ssid': ssid, 'server_cert_name': cert_file_name, 'password': password})

            print 'Closing connection.'
            curr_device.disconnect()

        # Go to the pairing devices page to add it to the DB. Does not really return the ajax call in case of success.
        return h.redirect_to(controller='devices', action='authorize', did=device_internal_id, cid=device.get_name())
