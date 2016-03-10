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

import datetime

from pylons import request, tmpl_context as c
from pylons import app_globals

from pycloud.pycloud.pylons.lib import helpers as h

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.manager.lib.pages import DevicesPage

from pycloud.pycloud.model.deployment import Deployment
from pycloud.pycloud.model.paired_device import PairedDevice

from pycloud.pycloud.ska.adb_ska_device import ADBSKADevice
from pycloud.pycloud.ska.bluetooth_ska_device import BluetoothSKADevice

################################################################################################################
# Controller for the page.
################################################################################################################
class DevicesController(BaseController):

    ############################################################################################################
    # Lists the stored devices, and allows to reset or to add more.
    ############################################################################################################
    def GET_list(self):
        c.devices_active = 'active'
        page = DevicesPage()

        # Ensure the device types are initialized.
        BluetoothSKADevice.initialize(app_globals.cloudlet.data_folder)
        ADBSKADevice.initialize(app_globals.cloudlet.data_folder)

        # Get the overall deployment info.
        page.deployment = Deployment.get_instance()
        if page.deployment.auth_start is None:
            page.deployment_auth_start = 'not set'
            page.deployment_auth_duration = 'not set'
            page.deployment_auth_end = 'not set'
        else:
            page.deployment_auth_start = page.deployment.auth_start.strftime('%Y-%m-%d %X')
            page.deployment_auth_duration = page.deployment.auth_duration
            page.deployment_auth_end = (page.deployment.auth_start + datetime.timedelta(minutes=page.deployment.auth_duration)).strftime('%Y-%m-%d %X')

        # Get the paired devices.
        page.paired_devices = PairedDevice.by_type('mobile')

        # Get the paired cloudlets.
        page.paired_cloudlets = PairedDevice.by_type('cloudlet')

        return page.render()

    ############################################################################################################
    # Clears all deployment info.
    ############################################################################################################
    def GET_clear(self):
        deployment = Deployment.get_instance()
        deployment.clear()
        deployment.remove()

        # Go to the main page.
        return h.redirect_to(controller='devices', action='list')

    ############################################################################################################
    # Bootstraps based on the remotely generated data by the pairing process.
    ############################################################################################################
    def POST_bootstrap(self):
        # Get the duration.
        # TODO: check when no duration is received, or an invalid duration is received.
        duration = int(request.params.get('duration', 0))

        # Setup initial configurations for each device type.
        BluetoothSKADevice.bootstrap()
        ADBSKADevice.bootstrap()

        deployment = Deployment.get_instance()
        deployment.bootstrap(duration)

        # Go to the main page.
        return h.redirect_to(controller='devices', action='list')

    ############################################################################################################
    #
    ############################################################################################################
    def GET_unpair(self, id):
        deployment = Deployment.get_instance()
        deployment.unpair_device(id)

        # Go to the main page.
        return h.redirect_to(controller='devices', action='list')

    ############################################################################################################
    #
    ############################################################################################################
    def GET_revoke(self, id):
        deployment = Deployment.get_instance()
        deployment.revoke_device(id)

        # Go to the main page.
        return h.redirect_to(controller='devices', action='list')

    ############################################################################################################
    #
    ############################################################################################################
    def GET_reauthorize(self, id):
        deployment = Deployment.get_instance()
        deployment.reauthorize_device(id)

        # Go to the main page.
        return h.redirect_to(controller='devices', action='list')
