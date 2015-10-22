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
import json
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

    ##################################################################################################################
    # Dummy function, used as a start response function for the controllers caled from this action, since we don't
    # want them to set the headers, as we will do that when we return.
    ##################################################################################################################
    def dummy_start_response(self, *args):
        pass

    #################################################################################################################
    # Helper function to abort with an encrypted reply.
    #################################################################################################################
    def encrypted_abort(self, code, message, password):
        print message
        encrypted_message = message #encryption.encrypt_message(message, password)
        abort(code, encrypted_message)

    #################################################################################################################
    # Main function of the encrypted API, receives a command and its parameters encrypted. Will call the corresponding
    # unecrypted controller, then encrypt its result and return the encrypted reply.
    #################################################################################################################
    def POST_command(self):
        # Check what device is sending this request.
        device_id = request.headers['X-Device-ID']
        print ''
        print 'Received encrypted request from device ' + device_id
        device_info = PairedDevice.by_id(device_id)
        if not device_info:
            # We can't encrypt the reply since we got an invalid device id.
            error = '#Device with id %s is not paired to this cloudlet' % device_id
            print error
            abort(401, error)

        # Get the device password.
        password = device_info.password

        # Check if device is authorized to send messages, and permission has not expired.
        if not device_info.auth_enabled:
            error = '#Authorization has been revoked for device with id %s' % device_id
            self.encrypted_abort(403, error, password)
        if device_info.auth_start + datetime.timedelta(minutes=device_info.auth_duration) < datetime.datetime.now():
            error = '#Authorization has expired for device with id %s' % device_id
            self.encrypted_abort(403, error, password)

        # Decrypt the request.
        encrypted_request = request.params['command']
        print 'Encrypted request: ' + encrypted_request
        decrypted_request = encryption.decrypt_message(encrypted_request, password)
        print 'Decrypted request: ' + decrypted_request

        # Parse the request.
        parts = decrypted_request.split("&")
        command = parts[0]
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
        reply_format = 'json'
        if command == '/services':
            controller = ServicesController()
            request.environ['pylons.routes_dict']['action'] = 'list'
            request.method = 'GET'
            reply = controller(self.environ, self.dummy_start_response)
        elif command == '/services/get':
            request.GET['serviceId'] = params_dict['serviceId']
            controller = ServicesController()
            request.environ['pylons.routes_dict']['action'] = 'find'
            request.method = 'GET'
            reply = controller(self.environ, self.dummy_start_response)
        elif command == '/servicevm/start':
            request.GET['serviceId'] = params_dict['serviceId']
            controller = ServiceVMController()
            request.environ['pylons.routes_dict']['action'] = 'start'
            request.method = 'GET'
            reply = controller(self.environ, self.dummy_start_response)

            # TODO: hack to store SVM id in DB along with paired device info.
            # Step 1: obtain SVM id from reply
            # Step 2: get device record with device_id, add svm_id (what to do if there was another one before?)
            # Step 3: start a threading.Timer to kill the VM when the mission ends?
        elif command == '/servicevm/stop':
            request.GET['instanceId'] = params_dict['instanceId']
            controller = ServiceVMController()
            request.environ['pylons.routes_dict']['action'] = 'stop'
            request.method = 'GET'
            reply = controller(self.environ, self.dummy_start_response)
        elif command == '/apps':
            for param in params_dict:
                request.GET[param] = params_dict[param]
            controller = AppPushController()
            request.environ['pylons.routes_dict']['action'] = 'getList'
            request.method = 'GET'
            reply = controller(self.environ, self.dummy_start_response)
        elif command == '/apps/get':
            request.GET['appId'] = params_dict['appId']
            controller = AppPushController()
            request.environ['pylons.routes_dict']['action'] = 'getApp'
            request.method = 'GET'
            reply = controller(self.environ, self.dummy_start_response)
            reply_format = 'binary'
        elif command == '/system':
            controller = CloudletController()
            request.environ['pylons.routes_dict']['action'] = 'metadata'
            request.method = 'GET'
            reply = controller(self.environ, self.dummy_start_response)
        else:
            self.encrypted_abort(404, '404 Not Found - command %s not found' % command, password)

        text_repy = reply[0]

        # Check if the reply is an error.
        if reply_format == 'json':
            try:
                json_object = json.loads(text_repy)
            except ValueError, e:
                print 'Error in repy: not a json object, assuming internal error. Will return a 500 error.'
                self.encrypted_abort(500, text_repy, password)

        # Encrypt the reply.
        # print 'Reply: ' + str(reply)
        encrypted_reply = encryption.encrypt_message(text_repy, password)
        print 'Encrypted reply' #: ' + encrypted_reply

        # Reset the response body that each controller may have added, and set the content length to the length of the
        # encrypted reply.
        response.body = ''
        response.content_length = len(encrypted_reply)

        # If there was no error, respond with OK and the encrypted reply.
        print 'Sending encrypted reply.'
        return encrypted_reply
