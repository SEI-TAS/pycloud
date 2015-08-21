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

# Pylon imports.
from pylons import request
from pylons.controllers.util import abort

# Controller to derive from.
from pycloud.pycloud.pylons.lib.base import BaseController

# Controllers to redirect to.
from pycloud.api.controllers.services import ServicesController
from pycloud.api.controllers.servicevm import ServiceVMController
from pycloud.api.controllers.apppush import AppPushController
from pycloud.api.controllers.cloudlet import CloudletController

from pycloud.pycloud.security import encryption
from pycloud.pycloud.model.paired_device import PairedDevice

################################################################################################################
# Class that handles all encrypted commands.
################################################################################################################
class EncryptedController(BaseController):

    def POST_command(self):
        # Check what device is sending this request.
        device_id = request.headers['X-Device-ID']
        device_info = PairedDevice.by_id(device_id)
        if not device_info:
            abort(404, '404 Not Found - device %s not found' % device_id)

        # Check if device is authorized to send messages, and permission has not expired.
        if not device_info.auth_enabled:
            abort(403, '403 Forbidden - authorization has been revoked for device %s' % device_id)
        if device_info.auth_start + datetime.timedelta(minutes=device_info.auth_duration) < datetime.datetime.now():
            abort(403, '403 Forbidden - authorization has expired for device %s' % device_id)

        # Decrypt the request.
        key = device_info.hash
        encrypted_request = request.params['request']
        decrypted_request = encryption.decrypt_message(encrypted_request, key)

        # Parse the request.
        parts = decrypted_request.split("&")
        command = parts[0]
        params = []
        if len(parts) > 1:
            params = parts[1:]

        # Then redirect to the appropriate controller.
        reply = ''
        if command == 'servicevm/listServices':
            reply = ServicesController.GET_list()
        elif command == 'servicevm/find':
            request.params['serviceId'] = params[0].split("=")[1]
            reply = ServicesController.GET_find()
        elif command == 'servicevm/start':
            request.params['serviceId'] = params[0].split("=")[1]
            reply = ServiceVMController.GET_start()
        elif command == 'servicevm/stop':
            request.params['instanceId'] = params[0].split("=")[1]
            reply = ServiceVMController.GET_start()
        elif command == 'app/getList':
            reply = AppPushController.GET_getList()
        elif command == 'app/getApp':
            request.params['app_id'] = params[0].split("=")[1]
            reply = AppPushController.GET_getApp()
        elif command == 'cloudlet_info':
            reply = CloudletController.GET_metadata()
        else:
            abort(404, '404 Not Found - command %s not found' % command)

        # Encrypt the reply and return it.
        encrypted_reply = encryption.encrypt_message(reply, key)
        return encrypted_reply
