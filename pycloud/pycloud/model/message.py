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

import datetime

from pycloud.pycloud.mongo import Model, ObjectID

################################################################################################################
# Represents a mailbox where messages to devices can be put.
################################################################################################################
class DeviceMessage(Model):
    # Meta class is needed so that minimongo can map this class onto the database.
    class Meta:
        collection = "messages"
        external = ['device_id', 'service_id', 'message', 'params']
        mapping = {
        }

    ################################################################################################################
    # Constructor.
    ################################################################################################################
    def __init__(self, *args, **kwargs):
        self.device_id = None
        self.service_id = None
        self.message = None
        self.params = {}
        self.datetime = datetime.datetime.now()
        self.read = False
        super(DeviceMessage, self).__init__(*args, **kwargs)

    ################################################################################################################
    # Locate a CommandMailbox by its ID.
    ################################################################################################################
    @staticmethod
    def by_id(item_id=None):
        record_id = item_id
        if not isinstance(record_id, ObjectID):
            # noinspection PyBroadException
            try:
                record_id = ObjectID(record_id)
            except:
                return None
        return DeviceMessage.find_one({'_id': record_id})

    ################################################################################################################
    # Locate a device by its pubilc device ID
    ################################################################################################################
    # noinspection PyBroadException
    @staticmethod
    def by_device_id(did=None):
        messages = []
        try:
            message_cursor = DeviceMessage.find({'device_id': did})
            for message in message_cursor:
                messages.append(message)
        except:
            pass
        return messages

    ################################################################################################################
    # Locate a device by its pubilc device ID
    ################################################################################################################
    # noinspection PyBroadException
    @staticmethod
    def unread_by_device_id(did=None):
        messages = []
        try:
            message_cursor = DeviceMessage.find({'device_id': did, 'read': False})
            for message in message_cursor:
                return_message = {}
                return_message['device_id'] = message['device_id']
                return_message['service_id'] = message['service_id']
                return_message['message'] = message['message']
                return_message['params'] = message['params']
                messages.append(return_message)
        except:
            pass
        return messages

    ################################################################################################################
    #
    ################################################################################################################
    # noinspection PyBroadException
    @staticmethod
    def mark_all_as_read(did=None):
        messages = []
        try:
            message_cursor = DeviceMessage.find({'device_id': did, 'read': False})
            for message in message_cursor:
                message['read'] = True
                message.save()
        except:
            pass
        return messages

    ################################################################################################################
    # Cleanly and safely gets a CommandMailbox and removes it from the database.
    ################################################################################################################
    @staticmethod
    def find_and_remove(item_id):
        # Find the right app and remove it. find_and_modify will only return the document with matching id.
        return DeviceMessage.find_and_modify(query={'_id': item_id}, remove=True)

################################################################################################################
# Particular message used to notify a device that it has to create a certain wifi profile and store credentials.
################################################################################################################
class AddTrustedCloudletDeviceMessage(DeviceMessage):

    MESSAGE = 'add-trusted-cloudlet'

    ################################################################################################################
    # Constructor.
    ################################################################################################################
    def __init__(self, paired_device_data_bundle, *args, **kwargs):
        super(AddTrustedCloudletDeviceMessage, self).__init__(*args, **kwargs)
        self.message = self.MESSAGE
        self.params = paired_device_data_bundle.__dict__


    ################################################################################################################
    #
    ################################################################################################################
    # noinspection PyBroadException
    @staticmethod
    def clear_messages(did=None):
        messages = AddTrustedCloudletDeviceMessage.find({'device_id': did, 'message': AddTrustedCloudletDeviceMessage.COMMAND})
        for message in messages:
            AddTrustedCloudletDeviceMessage.find_and_remove(message._id)
