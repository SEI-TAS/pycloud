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
__author__ = 'Dan'

import json
import os
import socket
import subprocess

from pycloud.pycloud.security.pairing_handler import PairingHandler
from pycloud.pycloud.ska import ska_constants
from pycloud.pycloud.ska.wifi_ska_comm import WiFiSKACommunicator
from ska_device_interface import ISKADevice


######################################################################################################################
# Checks that there is an enabled WiFi device, and returns its name.
######################################################################################################################
def get_adapter_name():
    internal_name = None

    cmd = subprocess.Popen('iw dev', shell=True, stdout=subprocess.PIPE)
    for line in cmd.stdout:
        if "Interface" in line:
            internal_name = line.split(' ')[1]
            internal_name = internal_name.replace("\n", "")
            break

    if internal_name is not None:
        print "WiFi adapter with name {} found".format(internal_name)
    else:
        print "WiFi adapter not found."

    return internal_name

######################################################################################################################
# Connects to a device given the device info dict, and returns a socket.
######################################################################################################################
def connect_to_device(host, port, name):
    print("Connecting to \"%s\" on %s" % (name, host))

    new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    new_socket.connect((host, port))

    print("Connected to \"%s\" on %s" % (name, host))

    return new_socket


######################################################################################################################
#
######################################################################################################################
class WiFiSKADevice(ISKADevice):

    ####################################################################################################################
    # Creates a device using the provided device info dict.
    ####################################################################################################################
    def __init__(self, device):
        self.device_info = device
        self.comm = None
        self.device_socket = None

    ####################################################################################################################
    # Returns a name for the device.
    ####################################################################################################################
    def get_name(self):
        return self.device_info['host']

    ####################################################################################################################
    # The port.
    ####################################################################################################################
    def get_port(self):
            return self.device_info['port']

    ####################################################################################################################
    # The friendly name.
    ####################################################################################################################
    def get_friendly_name(self):
            return self.device_info['name']

    ####################################################################################################################
    #
    ####################################################################################################################
    @staticmethod
    def initialize(root_folder):
        # Nothing to be done.
        pass

    ####################################################################################################################
    #
    ####################################################################################################################
    @staticmethod
    def bootstrap():
        # Nothing to be done.
        pass

    ####################################################################################################################
    # Returns a list of devices available.
    ####################################################################################################################
    @staticmethod
    def list_devices():
        # Check that there is an adapter available.
        adapter_address = get_adapter_name()
        if adapter_address is None:
            raise Exception("WiFi adapter not available.")

        # Find a device that has the service we want to use.
        # TODO: not implemented
        devices = []

        ska_devices = []
        for device in devices:
            ska_devices.append(WiFiSKADevice(device))

        return ska_devices

    ####################################################################################################################
    # Makes a TCP connection to the remote device.
    ####################################################################################################################
    def connect(self, host, port, name):
        self.device_socket = connect_to_device(host, port, name)
        if self.device_socket is None:
            return False
        else:
            self.comm = WiFiSKACommunicator(self.device_socket, self.device_info['secret'])
            return True

    ####################################################################################################################
    # Listen on a socket and handle commands. Each connection spawns a separate thread
    ####################################################################################################################
    def listen(self, files_path):
        adapter_name = get_adapter_name()
        if adapter_name is None:
            raise Exception("WiFi adapter not available.")

        self.device_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print((self.device_info['host'], self.device_info['port']))
        self.device_socket.bind((self.device_info['host'], self.device_info['port']))
        self.device_socket.listen(1)

        # Get new data until we get a final command.
        data_socket = None
        try:
            while True:
                data_socket, addr = self.device_socket.accept()
                self.comm = WiFiSKACommunicator(data_socket, self.device_info['secret'])
                handler = PairingHandler()

                try:
                    received_data = self.comm.receive_string()
                    message = json.loads(received_data)
                    print "Received a message."

                    if 'wifi_command' not in message:
                        raise Exception('Invalid message received: it does not contain a wifi_command field.')
                    command = message['wifi_command']

                    if command == "receive_file":
                        folder_path = handler.get_storage_folder_path(files_path, message)
                        self.receive_file(message, folder_path)

                    return_code, return_data = handler.handle_incoming(command, message, files_path)
                    if return_code == 'send':
                        self.__send_data(return_data)
                    elif return_code == 'ok':
                        self.__send_success_reply()
                    elif return_code == 'transfer_complete':
                        self.__send_success_reply()
                        break
                except Exception as e:
                    self.__send_error_reply(e.message)
        except:
            if data_socket is not None:
                data_socket.close()

    ####################################################################################################################
    # Closes the TCP socket.
    ####################################################################################################################
    def disconnect(self):
        if self.device_socket is not None:
            self.__send_command("transfer_complete", '')
            self.device_socket.close()

    ####################################################################################################################
    #
    ####################################################################################################################
    def get_data(self, data):
        result = self.__send_command('send_data', data)
        return self.__parse_result(result)

    ####################################################################################################################
    #
    ####################################################################################################################
    def send_data(self, data):
        result = self.__send_command('receive_data', data)
        return self.__parse_result(result)

    ####################################################################################################################
    # Sends a given file, ensuring the other side is ready to store it.
    ####################################################################################################################
    def send_file(self, file_path, file_id):
        result = self.__send_command('receive_file', {'file_id': file_id})
        if result == 'ack':
            # First send the file size in bytes.
            file_size = os.path.getsize(file_path)
            self.comm.send_string(str(file_size))
            reply = self.comm.receive_string()
            if reply == 'ack':
                self.comm.send_file(file_path)

                # Wait for final result.
                print 'Finished sending file. Waiting for result.'
                reply = self.comm.receive_string()
                return self.__parse_result(reply)

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
    # Sends a command.
    ####################################################################################################################
    def __send_command(self, command, data):
        # Prepare command.
        message = dict(data)
        message['wifi_command'] = command
        message['cloudlet_name'] = socket.gethostname()
        message_string = json.dumps(message)

        # Send command.
        self.comm.send_string(message_string)

        # Wait for reply, it should be small enough to fit in one chunk.
        reply = self.comm.receive_string()
        return reply

    ####################################################################################################################
    #
    ####################################################################################################################
    def __send_data(self, data_pair):
        data_key = data_pair[0]
        data_value = data_pair[1]
        self.comm.send_string(
            json.dumps({ska_constants.RESULT_KEY: ska_constants.SUCCESS, data_key: data_value}))

    ####################################################################################################################
    #
    ####################################################################################################################
    def __send_success_reply(self):
        self.comm.send_string(json.dumps({ska_constants.RESULT_KEY: ska_constants.SUCCESS}))

    ####################################################################################################################
    #
    ####################################################################################################################
    def __send_error_reply(self, error):
        self.comm.send_string(
            json.dumps({ska_constants.RESULT_KEY: ska_constants.ERROR, ska_constants.ERROR_MSG_KEY: error}))

    ####################################################################################################################
    # Checks the success of a result.
    ####################################################################################################################
    def __parse_result(self, result):
        # Check error and log it.
        json_data = json.loads(result)
        if json_data[ska_constants.RESULT_KEY] != ska_constants.SUCCESS:
            error_message = 'Error processing command on device: ' + json_data[ska_constants.ERROR_MSG_KEY]
            raise Exception(error_message)

        return json.loads(result)
