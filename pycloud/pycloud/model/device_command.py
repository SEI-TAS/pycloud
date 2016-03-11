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

from pycloud.pycloud.mongo import Model, ObjectID

################################################################################################################
# Represents a mailbox where commands to devices can be put.
################################################################################################################
class DeviceCommand(Model):
    # Meta class is needed so that minimongo can map this class onto the database.
    class Meta:
        collection = "commands"
        external = ['_id', 'device_id', 'service_id', 'command', 'params', 'datetime']
        mapping = {
        }

    ################################################################################################################
    # Constructor.
    ################################################################################################################
    def __init__(self, *args, **kwargs):
        self.device_id = None
        self.service_id = None
        self.command = None
        self.params = TrustedCloudletCredentials()
        self.datetime = None
        self.read = False
        super(DeviceCommand, self).__init__(*args, **kwargs)

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
        return DeviceCommand.find_one({'_id': record_id})

    ################################################################################################################
    # Locate a device by its pubilc device ID
    ################################################################################################################
    # noinspection PyBroadException
    @staticmethod
    def by_device_id(did=None):
        commands = []
        try:
            command_cursor = DeviceCommand.find({'device_id': did, 'read': True})
            for command in command_cursor:
                commands.append(command)
        except:
            pass
        return commands

    ################################################################################################################
    # Cleanly and safely gets a CommandMailbox and removes it from the database.
    ################################################################################################################
    @staticmethod
    def find_and_remove(item_id):
        # Find the right app and remove it. find_and_modify will only return the document with matching id.
        return DeviceCommand.find_and_modify(query={'_id': item_id}, remove=True)

################################################################################################################
#
################################################################################################################
class TrustedCloudletCredentials(object):

    ################################################################################################################
    # Constructor.
    ################################################################################################################
    def __init__(self, *args, **kwargs):
        self.ssid = None
        self.auth_password = None
        self.files = {}
        self.files['server_radius_cert'] = None
        self.files['server_public_key'] = None
        self.files['device_private_key'] = None

    ################################################################################################################
    # Loads a file.
    ################################################################################################################
    def load_file(self, file_type, file_path):
        with open(file_path, 'r') as input_file:
            self.files[file_type] = input_file.read()


################################################################################################################
# Particular command used to notify a device that it has to create a certain wifi profile and store credentials.
################################################################################################################
class AddTrustedCloudletDeviceCommand(DeviceCommand):

    ################################################################################################################
    # Constructor.
    ################################################################################################################
    def __init__(self, *args, **kwargs):
        super(AddTrustedCloudletDeviceCommand, self).__init__(*args, **kwargs)
        self.command = 'add-trusted-cloudlet'
