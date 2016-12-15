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
import subprocess

from pycloud.pycloud.cloudlet import Cloudlet
from pycloud.pycloud.security import radius
from pycloud.pycloud.model.cloudlet_credential import CloudletCredential


########################################################################################################################
#
########################################################################################################################
class PairingHandler(object):
    ####################################################################################################################
    # Create path and folders to store the files.
    ####################################################################################################################
    def get_storage_folder_path(self, base_path, message):
        folder_path = os.path.join(base_path, message['cloudlet_name'])
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        return folder_path

    ####################################################################################################################
    # Handle an incoming message.
    ####################################################################################################################
    def handle_incoming(self, command, message, files_path):
        return_code = 'ok'
        return_data = ''

        print 'Handling command ' + command
        if command == "receive_file":
            full_path = os.path.join(self.get_storage_folder_path(files_path, message), message['file_id'])

            if message['file_id'] == 'device.key':
                self.store_encryption_password(message['cloudlet_name'], full_path)
            elif message['file_id'] == radius.RADIUS_CERT_FILE_NAME:
                shutil.copy(full_path, '/etc/ca-certificates/')
        elif command == "receive_data":
            if 'command' not in message:
                raise Exception('Invalid message received: it does not contain a command field.')

            data_command = message['command']
            print 'Handling data command ' + data_command
            if data_command == "wifi-profile":
                try:
                    self.create_wifi_profile(message)
                except Exception as e:
                    print 'Error creating Wi-Fi profile: ' + str(e)
                    raise Exception(e.message)
            else:
                raise Exception('Unknown data command: ' + data_command)
        elif command == "send_data":
            if 'device_id' in message:
                return_code = 'send'
                return_data = ('device_id', Cloudlet.get_id())
            else:
                error_message = 'Unrecognized data request: ' + str(message)
                print error_message
                raise Exception(error_message)
        elif command == "transfer_complete":
            return_code = 'transfer_complete'
        else:
            error_message = 'Unrecognized command: ' + message['wifi_command']
            print error_message
            raise Exception(error_message)

        return return_code, return_data

    ####################################################################################################################
    #
    ####################################################################################################################
    def store_encryption_password(self, cloudlet_hostname, private_key_file_path):
        with open(private_key_file_path, 'r') as private_key_file:
            private_key = private_key_file.read()
        encryption_password = hashlib.sha256(private_key).hexdigest()

        # Clear previous creds for this cloudlet.
        CloudletCredential.find_and_remove(cloudlet_hostname)

        # Store new ones.
        credentials = CloudletCredential()
        credentials.cloudlet_fqdn = cloudlet_hostname
        credentials.encryption_password = encryption_password
        credentials.save()

    ####################################################################################################################
    # Create a wifi profile in /etc/NetworkManager/system-connections using system-connection-template.ini
    ####################################################################################################################
    def create_wifi_profile(self, message):
        print 'Creating Wi-Fi profile'
        with open("./wpa_supplicant/system-connection-template.ini", "r") as ini_file:
            file_data = ini_file.read()

        file_data = file_data.replace('$cloudlet-id', Cloudlet.get_id())
        file_data = file_data.replace('$ssid', message['ssid'])
        file_data = file_data.replace('$name', message['ssid'])
        file_data = file_data.replace('$password', message['password'])
        file_data = file_data.replace('$ca-cert', message['server_cert_name'])

        filename = os.path.join("/etc/NetworkManager/system-connections", message['ssid'])
        print 'Writing Wi-Fi profile to file ' + filename
        with open(filename, "w") as profile:
            profile.write(file_data)

        if os.path.exists(filename):
            print 'Wi-Fi profile file created'
        else:
            print 'Wi-Fi profile file NOT created!'

        # The file needs to be r/w only by user (root) to be used by Network Manager.
        print 'Setting profile as read/write only by owner (root)'
        command = "sudo chmod 600 " + filename
        cmd = subprocess.Popen(command, shell=True, stdout=None)
        cmd.wait()
        print 'Permissions changed'
