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

#import pycloud.pycloud.ska.ska_device_interface.ISKADevice
from ska_device_interface import ISKADevice

######################################################################################################################
# Checks that there is an enabled Bluetoothd evice, and returns its addresss.
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
    print('Searching for the SKA secure service')
    uuid = "fa87c0d0-afac-11de-8a39-0800200c9a66"
    service_matches = bluetooth.find_service(uuid=uuid, address=device_address)
    print 'Services found: ' + str(service_matches)

    if len(service_matches) == 0:
        print("couldn't find the SKA service =(")

    return service_matches

######################################################################################################################
#
######################################################################################################################
def connect_to_device(device_info):
    port = device_info["port"]
    name = device_info["name"]
    host = device_info["host"]

    print("Connecting to \"%s\" on %s" % (name, host))

    socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    socket.connect((host, port))

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

        # Wait for reply.
        reply = device_socket.recv(4096)
        print 'Reply: ' + str(reply)

######################################################################################################################
#
######################################################################################################################
class BluetoothSKADevice(ISKADevice):

    device_socket = None

    ####################################################################################################################
    #
    ####################################################################################################################
    def __init__(self, device):
        self.device_info = device

    ####################################################################################################################
    #
    ####################################################################################################################
    @staticmethod
    def list_devices():
        # Check that there is a Bluetooth adapter available.
        adapter_address = get_adapter_address()
        if adapter_address is None:
            return Exception("Bluetooth adapter not available.")

        # Find a device that has the service we want to use.
        devices = find_ska_service()

        ska_devices = []
        for device in devices:
            ska_devices.append(BluetoothSKADevice(device))

        return ska_devices

    ####################################################################################################################
    #
    ####################################################################################################################
    def connect(self):
        # Check that there is a Bluetooth adapter available.
        adapter_address = get_adapter_address()
        if adapter_address is None:
            raise Exception("Bluetooth adapter not available.")

        # Connect to the device.
        self.device_socket = connect_to_device(self.device_info)
        if self.device_socket is None:
            return False
        else:
            return True

    ####################################################################################################################
    #
    ####################################################################################################################
    def disconnect(self):
        if self.device_socket is not None:
            self.device_socket.close()

    ####################################################################################################################
    #
    ####################################################################################################################
    def get_id(self):
        if self.device_socket is None:
            raise Exception("Not connected to a device.")

        self.device_socket.send('id')

        # Wait for reply.
        device_id = self.device_socket.recv(4096)
        print 'Reply: ' + str(device_id)

        return device_id

    ####################################################################################################################
    #
    ####################################################################################################################
    def send_files(self, file_list):
        raise NotImplementedError()

######################################################################################################################
# "Main"
######################################################################################################################
def main():
    devices = BluetoothSKADevice.list_devices()

    if len(devices) < 0:
        sys.exit(0)

    device = devices[0]

    device.connect()
    device.get_id()
    device.disconnect()
