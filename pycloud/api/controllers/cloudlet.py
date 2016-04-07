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

__author__ = 'jdroot'

from pylons import request
from pylons.controllers.util import abort

from pycloud.pycloud.pylons.lib.base import BaseController, bool_param
from pycloud.pycloud.pylons.lib.util import asjson
from pycloud.pycloud.utils import timelog
from pycloud.pycloud.cloudlet import Cloudlet
from pycloud.pycloud.model import Service, App

from pycloud.pycloud.model.paired_device import PairedDevice
from pycloud.pycloud.model.message import DeviceMessage


class CloudletController(BaseController):

    # Maps API URL words to actual functions in the controller.
    API_ACTIONS_MAP = {'': {'action': 'metadata', 'reply_type': 'json'},
                       'get_messages': {'action': 'get_messages', 'reply_type': 'json'}}

    ################################################################################################################
    #
    ################################################################################################################
    @asjson
    def GET_metadata(self):
        timelog.TimeLog.reset()
        timelog.TimeLog.stamp("Request received: get metadata.")
        ret = Cloudlet.system_information()

        if bool_param('services'):
            ret.services = Service.find()

        if bool_param('apps'):
            ret.apps = App.find()

        timelog.TimeLog.stamp("Sending response back to " + request.environ['REMOTE_ADDR'])
        return ret

    ################################################################################################################
    # Only valid if the device has been paired, otherwise it will have no mailbox for commands.
    ################################################################################################################
    @asjson
    def GET_get_messages(self):
        device_id = request.headers['X-Device-ID']
        service_id = request.params.get('serviceId', None)

        messages = DeviceMessage.unread_by_device_id(device_id, service_id)
        reply = {}
        reply['messages'] = messages

        # Mark all commands as read, to avoid getting them again in a future call.
        DeviceMessage.mark_all_as_read(device_id, service_id)

        print 'Messages: '
        print reply
        return reply
