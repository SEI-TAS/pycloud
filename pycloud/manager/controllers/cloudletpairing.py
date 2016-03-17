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
from pycloud.manager.lib.pages import CloudletPairingPage
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
class CloudletPairingController(BaseController):

    ############################################################################################################
    # Entry point.
    ############################################################################################################
    def GET_index(self):
        return self.GET_available()

    ############################################################################################################
    # Lists the connected devices, and lets the system pair to one of them.
    ############################################################################################################
    def GET_available(self):
        page = CloudletPairingPage()
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
        connection = request.params.get('connection', None)
        if connection is None:
            connection = 'bt'

        try:
            # Create a device depending on the type.
            if connection == 'bt':
                port = request.params.get('port', None)
                name = request.params.get('name', None)
                curr_device = BluetoothSKADevice({'host': id, 'port': int(port), 'name': name})
            else:
                curr_device = ADBSKADevice(id)

            deployment = Deployment.get_instance()
            deployment.pair_device(curr_device)
        except Exception, e:
            return ajaxutils.show_and_return_error_dict(e.message)

        return ajaxutils.JSON_OK
