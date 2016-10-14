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

import os
import shutil
import hashlib

from pycloud.pycloud.cloudlet import Cloudlet
from pycloud.pycloud.security import radius
from pycloud.pycloud.model.cloudlet_credential import CloudletCredential


########################################################################################################################
#
########################################################################################################################
class WiFiSKAHandler(object):

    ####################################################################################################################
    # Handle an incoming message.
    ####################################################################################################################
    def handle_incoming(self, command, message, files_path):
        if command == "receive_file":
            full_path = os.path.join(files_path, message['file_id'])
            if message['file_id'] == 'device.key':
                self.store_encryption_password(message['cloudlet_name'], full_path)
                pass
            elif message['file_id'] == radius.RADIUS_CERT_FILE_NAME:
                shutil.copy(full_path, '/etc/ca-certificates/')
                pass

            return 'ok'
        elif command == "receive_data":
            if 'command' not in message:
                raise Exception('Invalid message received: it does not contain a command field.')

            data_command = message['command']
            if data_command == "wifi-profile":
                try:
                    self.create_wifi_profile(message)
                    return 'ok'
                except Exception as e:
                    print 'Error creating Wi-Fi profile: ' + str(e)
                    raise Exception(e.message)
            else:
                raise Exception('Unknown data command: ' + data_command)
        elif command == "send_data":
            if 'device_id' in message:
                return 'send', ('device_id', Cloudlet.get_id())
            else:
                error_message = 'Unrecognized data request: ' + str(message)
                print error_message
                raise Exception(error_message)
        elif command == "transfer_complete":
            return 'transfer_complete'
        else:
            error_message = 'Unrecognized command: ' + message['wifi_command']
            print error_message
            raise Exception(error_message)

    ####################################################################################################################
    #
    ####################################################################################################################
    def store_encryption_password(self, cloudlet_hostname, private_key_file_path):
        with open(private_key_file_path, 'r') as private_key_file:
            private_key = private_key_file.readall()
        encryption_password = hashlib.sha256(private_key).hexdigest()

        credentials = CloudletCredential()
        credentials.cloudlet_fqdn = cloudlet_hostname
        credentials.encryption_password = encryption_password
        credentials.save()

    ####################################################################################################################
    # Create a wifi profile in /etc/NetworkManager/system-connections using system-connection-template.ini
    ####################################################################################################################
    def create_wifi_profile(self, message):

        with open("./hostapd/system-connection-template.ini", "r") as ini_file:
            file_data = ini_file.read()

        file_data = file_data.replace('$cloudlet-id', message['ssid'])
        file_data = file_data.replace('$ssid', message['ssid'])
        file_data = file_data.replace('$name', message['ssid'])
        file_data = file_data.replace('$password', message['password'])
        file_data = file_data.replace('$ca-cert', message['server_cert_name'])

        filename = os.path.join("/etc/NetworkManager/system-connections", message['ssid'])
        with open(filename, "w") as profile:
            profile.write(file_data)
