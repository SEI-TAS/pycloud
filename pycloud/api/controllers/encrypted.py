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
from pylons import request, response
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
    
    def fake_start_response(self, *args):
        pass

    def POST_command(self):
        # Check what device is sending this request.
        device_id = request.headers['X-Device-ID']
        print 'Received request from device ' + device_id
        device_info = PairedDevice.by_id(device_id)
        if not device_info:
            abort(404, '404 Not Found - device %s not found' % device_id)

        # Check if device is authorized to send messages, and permission has not expired.
        if not device_info.auth_enabled:
            print 'Authorization has been revoked for device %s' % device_id
            abort(403, '403 Forbidden - authorization has been revoked for device %s' % device_id)
        if device_info.auth_start + datetime.timedelta(minutes=device_info.auth_duration) < datetime.datetime.now():
            print 'Authorization has expired for device %s' % device_id
            abort(403, '403 Forbidden - authorization has expired for device %s' % device_id)

        # Decrypt the request.
        password = device_info.password
        encrypted_request = request.params['command']
        print 'Encrypted request: ' + encrypted_request
        decrypted_request = encryption.decrypt_message(encrypted_request, password)
        print 'Decrypted request: ' + decrypted_request

        # Parse the request.
        parts = decrypted_request.split("&")
        command = parts[0]
        params = []
        if len(parts) > 1:
            params = parts[1:]
            params_dict = {}
            for param in params:
                key = param.split("=")[0]
                value = param.split("=")[1]
                params_dict[key] = value

        # Then redirect to the appropriate controller.
        print 'Received command: ' + command
        reply = ''
        if command == '/servicevm/listServices':
            controller = ServicesController()
            request.environ['pylons.routes_dict']['action'] = 'list'
            request.method = 'GET'
            reply = controller(self.environ, self.fake_start_response)
        elif command == '/servicevm/find':
            request.GET['serviceId'] = params_dict['serviceId']
            controller = ServicesController()
            request.environ['pylons.routes_dict']['action'] = 'find'
            request.method = 'GET'
            reply = controller(self.environ, self.fake_start_response)
        elif command == '/servicevm/start':
            request.GET['serviceId'] = params_dict['serviceId']
            controller = ServiceVMController()
            request.environ['pylons.routes_dict']['action'] = 'start'
            request.method = 'GET'
            reply = controller(self.environ, self.fake_start_response)
        elif command == '/servicevm/stop':
            request.GET['instanceId'] = params_dict['instanceId']
            controller = ServiceVMController()
            request.environ['pylons.routes_dict']['action'] = 'stop'
            request.method = 'GET'
            reply = controller(self.environ, self.fake_start_response)
        elif command == '/app/getList':
            for param in params_dict:
                request.GET[param] = params_dict[param]
            controller = AppPushController()
            request.environ['pylons.routes_dict']['action'] = 'getList'
            request.method = 'GET'
            reply = controller(self.environ, self.fake_start_response)
        elif command == '/app/getApp':
            request.GET['app_id'] = params_dict['app_id']
            controller = AppPushController()
            request.environ['pylons.routes_dict']['action'] = 'getApp'
            request.method = 'GET'
            reply = controller(self.environ, self.fake_start_response)
        elif command == '/cloudlet_info':
            controller = CloudletController()
            request.environ['pylons.routes_dict']['action'] = 'metadata'
            request.method = 'GET'
            reply = controller(self.environ, self.fake_start_response)
        else:
            abort(404, '404 Not Found - command %s not found' % command)

        # Encrypt the reply and return it.
        print 'Reply: ' + str(reply)
        encrypted_reply = encryption.encrypt_message(reply[0], password)
        print 'Encrypted reply: ' + encrypted_reply

        # Reset the response body that each controller may have added, and set the content length to the length of the
        # encrypted reply.
        response.body = ''
        response.content_length = len(encrypted_reply)

        return encrypted_reply
