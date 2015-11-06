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

"""
A simple Python script to send messages to a server over Bluetooth
using PyBluez (with Python 2).
"""

import bluetooth
import sys
import subprocess
import os
import json

from ska_device_interface import ISKADevice
from pycloud.pycloud.ska import ska_constants

# Id of the service on a mobile device that is waiting for a pairing process.
SKA_PAIRING_UUID = "fa87c0d0-afac-11de-8a39-0800200c9a66"

# Size of a chunk when transmitting through TCP .
CHUNK_SIZE = 4096

######################################################################################################################
# Checks that there is an enabled Bluetooth device, and returns its address.
######################################################################################################################
def get_adapter_address():
    internal_address = None
    cmd = subprocess.Popen('hciconfig', shell=True, stdout=subprocess.PIPE)
    for line in cmd.stdout:
        if "BD Address" in line:
            internal_address = line.split(' ')[2]

    if internal_address is not None:
        print "Bluetooth adapter with address {} found".format(internal_address)
    else:
        print "Bluetooth adapter not found."

    return internal_address

######################################################################################################################
#
######################################################################################################################
def find_bluetooth_devices():
    print('Finding bluetooth devices')
    devices = bluetooth.discover_devices(duration=3, lookup_names=True)
    print 'Devices found: ' + str(devices)
    return devices

######################################################################################################################
#
######################################################################################################################
def find_ska_service(device_address=None):
    print('Searching for devices with the SKA secure service')
    service_matches = bluetooth.find_service(uuid=SKA_PAIRING_UUID, address=device_address)
    print 'Services found: ' + str(service_matches)

    if len(service_matches) == 0:
        print("couldn't find the SKA service =(")

    return service_matches

######################################################################################################################
# Pairs to a device, trying to force numeric comparison.
######################################################################################################################
def pair_through_numeric_comparison(device_info):
    pass
    # Register an agent to handle pairing.
    # TODO: is this really needed on Ubuntu? Don't we have an agent already? How to set up its capabilities?
    #bus = dbus.SystemBus()
    #obj = bus.get_object('org.bluez', '/org/bluez')
    #manager = dbus.Interface(obj, "org.bluez.AgentManager1")
    #manager.RegisterAgent(path, 'DisplayYesNo')

    #
    #import bluezutils
    #device = bluezutils.find_device(device_info['host'], 'hci0')
    #device.Pair(reply_handler=pair_reply, error_handler=pair_error, timeout=60000)


######################################################################################################################
# Connects to a Bluetooth device given the bluetooth device info dict, and returns a socket.
######################################################################################################################
def connect_to_device(host, port, name):
    print("Connecting to \"%s\" on %s" % (name, host))

    # TODO: test pairing manually through d-bus here, before opening socket through Pybluez.
    # Seems to be only way to configure agent capabilities.

    socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    socket.connect((host, port))

    print("Connected to \"%s\" on %s" % (name, host))

    return socket

######################################################################################################################
#
######################################################################################################################
def comm_test(device_socket):
    print('type: ')
    while 1:
        text = raw_input()
        if text == "quit":
            break
        if text == "get_id":
            print('Getting id...')
        device_socket.send(text)

        # Wait for reply, it should be small enough to fit in one chunk.
        reply = device_socket.recv(CHUNK_SIZE)
        print 'Id: ' + str(reply)

######################################################################################################################
#
######################################################################################################################
class BluetoothSKADevice(ISKADevice):

    device_socket = None
    device_info = None

    ####################################################################################################################
    # Creates a device using the provided device info dict.
    ####################################################################################################################
    def __init__(self, device):
        self.device_info = device

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
    # Returns a list of BluetoothSKADevices that have the SKA Pairing service available.
    ####################################################################################################################
    @staticmethod
    def list_devices():
        # Check that there is a Bluetooth adapter available.
        adapter_address = get_adapter_address()
        if adapter_address is None:
            raise Exception("Bluetooth adapter not available.")

        # Find a device that has the service we want to use.
        devices = find_ska_service()

        ska_devices = []
        for device in devices:
            ska_devices.append(BluetoothSKADevice(device))

        return ska_devices

    ####################################################################################################################
    # Makes a TCP connection over Bluetooth to this device.
    ####################################################################################################################
    def connect(self):
        # Check that there is a Bluetooth adapter available.
        adapter_address = get_adapter_address()
        if adapter_address is None:
            raise Exception("Bluetooth adapter not available.")
        # Connect to the device.
        self.device_socket = connect_to_device(self.device_info['host'], self.device_info['port'], self.device_info['name'])
        if self.device_socket is None:
            return False
        else:
            return True

    ####################################################################################################################
    # Closes the TCP socket.
    ####################################################################################################################
    def disconnect(self):
        if self.device_socket is not None:
            self.device_socket.close()

    ####################################################################################################################
    #
    ####################################################################################################################
    def get_data(self, data):
        message = dict(data)
        message['bt_command'] = 'send_data'
        message_string = json.dumps(message)

        result = self.send_command(message_string)

        # Check error and log it.
        json_data = json.loads(result)
        if json_data[ska_constants.RESULT_KEY] != ska_constants.SUCCESS:
            error_messge = 'Error processing command on device: ' + json_data[ska_constants.ERROR_MSG_KEY]
            raise Exception(error_messge)

        return json.loads(result)

    ####################################################################################################################
    #
    ####################################################################################################################
    def send_data(self, data):
        message = dict(data)
        message['bt_command'] = 'receive_data'
        message_string = json.dumps(message)
        result = self.send_command(message_string)

        # Check error and log it.
        json_data = json.loads(result)
        if json_data[ska_constants.RESULT_KEY] != ska_constants.SUCCESS:
            error_messge = 'Error processing command on device: ' + json_data[ska_constants.ERROR_MSG_KEY]
            raise Exception(error_messge)


    ####################################################################################################################
    # Sends a short command.
    ####################################################################################################################
    def send_command(self, command):
        if self.device_socket is None:
            raise Exception("Not connected to a device.")

        print 'Sending command message: ' + command
        self.device_socket.send(command)

        # Wait for reply, it should be small enough to fit in one chunk.
        reply = self.device_socket.recv(CHUNK_SIZE)
        print 'Reply: ' + reply
        return reply

    ####################################################################################################################
    # Sends a given file, ensuring the other side is ready to store it.
    ####################################################################################################################
    def send_file(self, file_path, file_id):
        message = {'bt_command': 'receive_file', 'file_id': file_id}
        message_string = json.dumps(message)

        ack = self.send_command(message_string)
        if ack == 'ack':
            # First send the file size in bytes.
            file_size = os.path.getsize(file_path)
            ack = self.send_command(str(file_size))
            if ack == 'ack':
                # Open and send the file in chunks.
                print 'Sending file.'
                file_to_send = open(file_path, 'rb')

                # Send until there is no more data in the file.
                while True:
                    data_chunk = file_to_send.read(CHUNK_SIZE)
                    if not data_chunk:
                        break

                    sent = self.device_socket.send(data_chunk)
                    if sent < len(data_chunk):
                        print 'Error sending data chunk.'

                print 'Finished sending file. Waiting for result.'

                # Wait for reply, it should be small enough to fit in one chunk.
                reply = self.device_socket.recv(CHUNK_SIZE)
                print 'Reply: ' + reply

                # Check error and log it.
                json_data = json.loads(reply)
                if json_data[ska_constants.RESULT_KEY] != ska_constants.SUCCESS:
                    error_messge = 'Error processing command on device: ' + json_data[ska_constants.ERROR_MSG_KEY]
                    raise Exception(error_messge)

######################################################################################################################
# Test method
######################################################################################################################
def test():
    devices = BluetoothSKADevice.list_devices()

    if len(devices) < 0:
        sys.exit(0)

    device = devices[0]

    device.connect()
    device.get_id()
    device.disconnect()
