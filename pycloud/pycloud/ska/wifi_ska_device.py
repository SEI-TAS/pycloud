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

import socket
import time
import os
from tempfile import mkstemp

from wifi_ska_comm import WiFiSKACommunicator, WiFiAdapter
from ska_device_interface import ISKADevice


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
        adapter_address = WiFiAdapter().get_adapter_name()
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
    def connect(self, retries=5):
        while retries > 0:
            try:
                self.device_socket = connect_to_device(self.device_info['host'], self.device_info['port'], self.device_info['name'])
            except Exception as e:
                error_message = 'Error connecting to IP {}: ({}) - {}'.format(self.device_info['host'], type(e).__name__, str(e))
                print error_message

            if self.device_socket is not None:
                self.comm = WiFiSKACommunicator(self.device_socket, self.device_info['secret'])
                return True
            else:
                retries -= 1
                retry_wait_seconds = 5
                print 'Waiting to retry connection...'
                time.sleep(retry_wait_seconds)

        print 'Could not connect to server.'
        return False

    ####################################################################################################################
    # Closes the TCP socket.
    ####################################################################################################################
    def disconnect(self):
        if self.device_socket is not None:
            self.comm.send_command('transfer_complete', '')
            self.device_socket.close()

    ####################################################################################################################
    #
    ####################################################################################################################
    def get_data(self, data):
        result = self.comm.send_command('send_data', data)
        return self.comm.parse_result(result)

    ####################################################################################################################
    #
    ####################################################################################################################
    def send_data(self, data):
        result = self.comm.send_command('receive_data', data)
        return self.comm.parse_result(result)

    ####################################################################################################################
    # Sends a given file, ensuring the other side is ready to store it.
    ####################################################################################################################
    def send_file(self, file_path, file_id):
        if os.path.getsize(file_path) == 0:
            print 'Empty file, not sending data.'
            return

        result = self.comm.send_command('receive_file', {'file_id': file_id})
        if result == 'ack':
            reply = self.comm.send_file(file_path)
            return self.comm.parse_result(reply)


######################################################################################################################
# Test method
######################################################################################################################
def test():
    # Connect to the server (cloudlet) in the network.
    remote_cloudlet_name = "WiFiServer"
    remote_cloudlet = WiFiSKADevice({'host': '127.0.0.1', 'port': 1700,
                                     'name': remote_cloudlet_name, 'secret': 'secret'})
    successful_connection = remote_cloudlet.connect()
    if not successful_connection:
        raise Exception("Could not connect to cloudlet")

    try:
        id_data = remote_cloudlet.get_data({'device_id': 'none'})
        device_internal_id = id_data['device_id']
        print 'Device id: ' + device_internal_id

        print('Sending command: test_command')
        result = remote_cloudlet.send_data({'command': 'test_command'})
        print 'Result: ' + str(result)

        print('Sending file: test_file')
        test_file_descriptor, test_file_path = mkstemp(text=True)
        with open(test_file_path, 'w') as test_file:
            for i in range(0, 1000):
                test_file.write('some_test_data ')
        result = remote_cloudlet.send_file(test_file_path, 'test_file')
        print 'Result: ' + str(result)
        import os
        os.remove(test_file_path)
    except Exception as e:
        print 'Error: ' + str(e)
    finally:
        remote_cloudlet.disconnect()
