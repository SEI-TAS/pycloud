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

from pylons import request, response, session, tmpl_context as c
from pylons import app_globals

from pycloud.pycloud.pylons.lib import helpers as h
from pycloud.pycloud.pylons.lib.util import asjson
from pycloud.pycloud.utils import ajaxutils

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.manager.lib.pages import DevicesPage

from pycloud.pycloud.model.deployment import Deployment
from pycloud.pycloud.model.paired_device import PairedDevice

from pycloud.pycloud.ska.adb_ska_device import ADBSKADevice
from pycloud.pycloud.ska.bluetooth_ska_device import BluetoothSKADevice

from pycloud.pycloud.ibc import radius

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

        # Get the overall deployment info.
        page.deployment = Deployment.find_one()
        if page.deployment is None:
            page.deployment_auth_start = 'not set'
            page.deployment_auth_duration = 'not set'
        else:
            page.deployment_auth_start = page.deployment.auth_start.strftime('%Y-%m-%d %X')
            page.deployment_auth_duration = page.deployment.auth_duration

        # Get the paired devices.
        page.paired_devices = PairedDevice.find()

        return page.render()

    ############################################################################################################
    # Clears all deployment info.
    ############################################################################################################
    def GET_clear(self):
        # Remove all data from DB.
        PairedDevice.clear_data()
        Deployment.remove()

        # Go to the main page.
        return h.redirect_to(controller='devices', action='list')

    ############################################################################################################
    # Boostraps based on the remotely generated data by the pairing process.
    ############################################################################################################
    def POST_bootstrap(self):
        # Get the duration.
        # TODO: check when no duration is received, or an invalid duration is received.
        duration = int(request.params.get('duration', 0))
        print duration

        # Remove all data from DB.
        PairedDevice.clear_data()
        Deployment.remove()

        # Setup general device configurations.
        BluetoothSKADevice.setup(app_globals.cloudlet.data_folder)
        ADBSKADevice.setup(app_globals.cloudlet.data_folder)

        # TODO: Create server keys.
        # server_keys = ServerCredentials()
        # server_keys.create_key()

        # Create RADIUS server certificate.
        radius.generate_certificate()

        # Set up a new deployment.
        deployment = Deployment()
        deployment.auth_start = datetime.datetime.now()
        deployment.auth_duration = duration
        deployment.save()

        # Go to the main page.
        return h.redirect_to(controller='devices', action='list')

    ############################################################################################################
    # NOTE: this should be called from the SKA pairing process.
    ############################################################################################################
    @asjson
    def GET_authorize(self, did):
        cid = request.params.get('cid', None)

        # Create a new paired device with the id info we just received.
        print 'Adding paired device to DB.'
        paired_device = PairedDevice()
        paired_device.device_id = did
        paired_device.connection_id = cid

        # By default, authorization for a device will be the same as the deployment info.
        deployment = Deployment.find_one()
        paired_device.auth_start = deployment.auth_start
        paired_device.auth_duration = deployment.auth_duration
        paired_device.auth_enabled = True

        # Store the paired device.
        paired_device.save()

        # Go to the main page.
        print 'Device added to DB.'
        return ajaxutils.JSON_OK

    ############################################################################################################
    #
    ############################################################################################################
    def GET_unpair(self, id):
        # Remove it from the list.
        PairedDevice.find_and_remove(id)

        # Go to the main page.
        return h.redirect_to(controller='devices', action='list')

    ############################################################################################################
    #
    ############################################################################################################
    def GET_revoke(self, id):
        # Mark it as disabled.
        paired_device = PairedDevice.by_id(id)
        paired_device.auth_enabled = False
        paired_device.save()

        # Go to the main page.
        return h.redirect_to(controller='devices', action='list')

    ############################################################################################################
    #
    ############################################################################################################
    def GET_reauthorize(self, id):
        # Mark it as enabled.
        paired_device = PairedDevice.by_id(id)
        paired_device.auth_enabled = True
        paired_device.save()

        # Go to the main page.
        return h.redirect_to(controller='devices', action='list')
