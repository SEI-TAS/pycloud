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
import threading

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
    # Dummy function, used as a start response function for the controllers called from this action, since we don't
    # want them to set the headers, as we will do that when we return.
    ##################################################################################################################
    def dummy_start_response(self, *args):
        pass

    #################################################################################################################
    # Helper function to abort.
    #################################################################################################################
    def send_abort_response(self, code, message, password):
        print message
        encrypted_message = message
        #encrypted_message = encryption.encrypt_message(message, password)
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
            self.send_abort_response(401, '#Device with id %s is not paired to this cloudlet' % device_id, None)

        # Get the device password.
        password = device_info.password

        # Check if device is authorized to send messages, and permission has not expired.
        if not device_info.auth_enabled:
            error = '#Authorization has been revoked for device with id %s' % device_id
            self.send_abort_response(403, error, password)
        if device_info.auth_start + datetime.timedelta(minutes=device_info.auth_duration) < datetime.datetime.now():
            error = '#Authorization has expired for device with id %s' % device_id
            self.send_abort_response(403, error, password)

        # Decrypt the request.
        encrypted_request = request.params['command']
        print 'Encrypted request: ' + encrypted_request
        decrypted_request = encryption.decrypt_message(encrypted_request, password)
        print 'Decrypted request: ' + decrypted_request

        # Parse the request.
        controller_name = None
        action_name = ''
        parts = decrypted_request.split("&")
        command = parts[0]
        print 'Received command: ' + command
        command_parts = command.split("/")
        if len(command_parts) > 1:
            controller_name = command_parts[1]
        if len(command_parts) > 2:
            action_name = command_parts[2]

        # Parse params, if any.
        params_dict = {}
        if len(parts) > 1:
            params = parts[1:]
            for param in params:
                key = param.split("=")[0]
                value = param.split("=")[1]
                params_dict[key] = value

        # Find the appropriate controller.
        controller = None
        if controller_name == 'services':
            controller = ServicesController()
        elif controller_name == 'servicevm':
            controller = ServiceVMController()
        elif controller_name == 'apps':
            controller = AppPushController()
        elif controller_name == 'system':
            controller = CloudletController()

        is_invalid_command = controller is None or action_name not in controller.API_ACTIONS_MAP
        if is_invalid_command:
            self.send_abort_response(404, '#Command %s not found' % command, password)

        # Prepare the unencrypted request we are redirecting to, and execute it.
        reply_format = 'json'
        request.method = 'GET'
        for param in params_dict:
            request.GET[param] = params_dict[param]
        request.environ['pylons.routes_dict']['action'] = controller.API_ACTIONS_MAP[action_name]['action']
        internal_response = controller(self.environ, self.dummy_start_response)
        raw_response = internal_response[0]

        # TODO: find a way to make this hack cleaner....
        # Hack to store SVM id in DB along with paired device info to stop it when mission ends.
        if controller_name == 'servicevm' and action_name == 'start':
            associate_instance_to_device(device_info, raw_response)

        # Check if the reply is an error.
        if reply_format == 'json':
            try:
                json.loads(raw_response)
            except ValueError:
                print 'Error in reply: not a json object, assuming internal error. Will return a 500 error.'
                self.send_abort_response(500, raw_response, password)

        # Encrypt the reply.
        encrypted_reply = encryption.encrypt_message(raw_response, password)
        print 'Encrypted reply'

        # Reset the response body that each controller may have added, and set the content length to the length of the
        # encrypted reply.
        response.body = ''
        response.content_length = len(encrypted_reply)

        # If there was no error, respond with OK and the encrypted reply.
        print 'Sending encrypted reply.'
        return encrypted_reply


################################################################################################################
# Stores the instance id of a running Service VM instance associated with a paired device.
################################################################################################################
def associate_instance_to_device(device_info, reply):
    try:
        json_object = json.loads(reply)
        instance_id = json_object['_id']

        # Store the instance info in the DB.
        device_info.instance = instance_id
        device_info.save()
    except ValueError:
        print 'VM not started, will not be stored to be stopped later.'
        return

    # Start a timer to stop the instance when the mission time ends.
    time_to_wait = ((device_info.auth_start + datetime.timedelta(minutes=device_info.auth_duration)) - datetime.datetime.now()).seconds
    if time_to_wait > 0:
        print 'Setting up timer to stop Service VM once deployment time runs out (time to wait: ' + str(time_to_wait) + ' seconds)'
        timer_thread = threading.Timer(time_to_wait, device_info.stop_associated_instance, [device_info.device_id])
        timer_thread.start()
    else:
        # If we are already past end time, stop VM right away.
        print 'Stopping service VM right away since deployment has already timed out.'
        device_info.stop_associated_instance()
