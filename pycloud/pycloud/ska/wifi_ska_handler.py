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
import json

from pycloud.pycloud.ska import ska_constants
from pycloud.pycloud.cloudlet import Cloudlet
from pycloud.pycloud.ska.wifi_ska_comm import WiFiSKACommunicator


########################################################################################################################
#
########################################################################################################################
class WiFiSKAHandler(object):

    ####################################################################################################################
    #
    ####################################################################################################################
    def __init__(self, data_socket, encryption_secret):
        self.data_socket = data_socket
        self.encryption_secret = encryption_secret
        self.comm = WiFiSKACommunicator(self.data_socket, self.encryption_secret)

    ####################################################################################################################
    # Handle an incoming message.
    ####################################################################################################################
    def handle_incoming(self):
        try:
            received_data = self.comm.receive_string()
            message = json.loads(received_data)
            print "Got data"

            if 'wifi_command' not in message:
                self.__send_error_reply('Invalid message received.')

            command = message['wifi_command']
            if command == "receive_file":
                # TODO: set base path
                self.receive_file(message, '')
                self.__send_success_reply()
            elif command == "receive_data":
                if 'command' not in message:
                    self.__send_error_reply('Invalid message received.')

                data_command = message['command']
                if data_command == "wifi-profile":
                    try:
                        self.create_wifi_profile(message)
                        self.__send_success_reply()
                    except Exception as e:
                        print 'Error creating Wi-Fi profile: ' + str(e)
                        self.__send_error_reply(e.message)
                else:
                    self.__send_error_reply('Unknown data command: ' + data_command)
            elif command == "send_data":
                if 'device_id' in message:
                    self.__send_data('device_id', Cloudlet.get_id())
                else:
                    error_message = 'Unrecognized data request: ' + str(message)
                    print error_message
                    self.__send_error_reply(error_message)
            elif command == "transfer_complete":
                self.__send_success_reply()
                return "transfer_complete"
            else:
                error_message = 'Unrecognized command: ' + message['wifi_command']
                print error_message
                self.__send_error_reply(error_message)
        finally:
            self.data_socket.close()

        return 'ok'

    ####################################################################################################################
    #
    ####################################################################################################################
    def __send_data(self, data_key, data_value):
        self.comm.send_string(json.dumps({ska_constants.RESULT_KEY: ska_constants.SUCCESS, data_key: data_value}))

    ####################################################################################################################
    #
    ####################################################################################################################
    def __send_success_reply(self):
        self.comm.send_string(json.dumps({ska_constants.RESULT_KEY: ska_constants.SUCCESS}))

    ####################################################################################################################
    #
    ####################################################################################################################
    def __send_error_reply(self, error):
        self.comm.send_string(json.dumps({ska_constants.RESULT_KEY: ska_constants.ERROR, ska_constants.ERROR_MSG_KEY: error}))

    ####################################################################################################################
    #
    ####################################################################################################################
    def receive_file(self, message, base_path):
        self.comm.send_string('ack')
        size = self.comm.receive_string()
        if size > 0:
            file_path = os.path.join(base_path, message['file_id'])
            self.comm.receive_file(file_path)

    ####################################################################################################################
    # Create a wifi profile in /etc/NetworkManager/system-connections using system-connection-template.ini
    ####################################################################################################################
    def create_wifi_profile(self, message):

        with open("./system-connection-template.ini", "r") as ini_file:
            file_data = ini_file.read()

        file_data = file_data.replace('$ssid', message['ssid'])
        file_data = file_data.replace('$name', message['cloudlet_name'])
        file_data = file_data.replace('$password', message['password'])
        file_data = file_data.replace('$ca-cert', message['server_cert_name'])

        filename = "/etc/NetworkManager/system-connections" + message['cloudlet-name']
        with open(filename, "w") as profile:
            profile.write(file_data)
