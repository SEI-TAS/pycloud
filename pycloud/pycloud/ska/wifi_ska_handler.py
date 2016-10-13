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

from pycloud.pycloud.cloudlet import Cloudlet


########################################################################################################################
#
########################################################################################################################
class WiFiSKAHandler(object):

    ####################################################################################################################
    # Handle an incoming message.
    ####################################################################################################################
    def handle_incoming(self, message):
        if 'wifi_command' not in message:
            raise Exception('Invalid message received: it does not contain a wifi_command field.')

        command = message['wifi_command']
        if command == "receive_file":
            # TODO: generate and store encryption key when file id is 'device.key'
            # TODO: store certificate in /etc/ca-certificates/ when id is radius.RADIUS_CERT_FILE_NAME
            return 'file'
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
            return "transfer_complete"
        else:
            error_message = 'Unrecognized command: ' + message['wifi_command']
            print error_message
            raise Exception(error_message)

    ####################################################################################################################
    # Create a wifi profile in /etc/NetworkManager/system-connections using system-connection-template.ini
    ####################################################################################################################
    def create_wifi_profile(self, message):

        with open("./hostapd/system-connection-template.ini", "r") as ini_file:
            file_data = ini_file.read()

        file_data = file_data.replace('$cloudlet-id', Cloudlet.get_id())
        file_data = file_data.replace('$ssid', message['ssid'])
        file_data = file_data.replace('$name', message['ssid'])
        file_data = file_data.replace('$password', message['password'])
        file_data = file_data.replace('$ca-cert', message['server_cert_name'])

        filename = os.path.join("/etc/NetworkManager/system-connections", message['ssid'])
        with open(filename, "w") as profile:
            profile.write(file_data)
