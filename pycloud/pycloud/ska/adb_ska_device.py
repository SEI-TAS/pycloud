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
A simple Python script to
"""

import time
import json

from adb.usb_exceptions import AdbCommandFailureException
from adb.adb_commands import AdbCommands, M2CryptoSigner

from ska_device_interface import ISKADevice

REMOTE_FOLDER = '/sdcard/cloudlet/adb/'

IN_DATA_SERVICE = 'edu.cmu.sei.cloudlet.client/.ska.adb.InDataService'

IN_FILE_SERVICE = 'edu.cmu.sei.cloudlet.client/.ska.adb.StoreFileService'
IN_FILE_REMOTE_FILEPATH = REMOTE_FOLDER + 'in_file'

OUT_DATA_SERVICE = 'edu.cmu.sei.cloudlet.client/.ska.adb.OutDataService'
OUT_DATA_REMOTE_FILEPATH = REMOTE_FOLDER + 'out_data.json'

######################################################################################################################
# Attempts to connect to an ADB daemon on a given USB device. Returns a proxy to that daemon if successful, or None if
# unsuccessful.
######################################################################################################################
def connect_to_adb_daemon(device):
    # Load host keypair to authenticate with ADB daemon.
    keySigner = M2CryptoSigner('adbkey')

    try:
        print 'Connecting to USB device'
        device.Open()

        print 'Connecting to ADB daemon'
        adbDaemon = AdbCommands.Connect(device, banner="cloudlet", rsa_keys=[keySigner], auth_timeout_ms=15000)
        return adbDaemon
    except Exception, e:
        print e
        return None

######################################################################################################################
#
######################################################################################################################
def disconnect_from_adb_daemon(adbDaemon):
    adbDaemon.Close()

######################################################################################################################
# Starts the given service on the given daemon.
######################################################################################################################
def start_service(adbDaemon, service_name, extras={}):
    command = 'am startservice -n ' + service_name
    for extra_key in extras:
        command += ' -e ' + extra_key + ' ' + extras[extra_key]
    print command
    adbDaemon.Shell(command, timeout_ms=20000)

######################################################################################################################
# Implementation of a SKA device through ADB.
######################################################################################################################
class ADBSKADevice(ISKADevice):

    serial_number = None
    adb_daemon = None

    ####################################################################################################################
    # Creates a device using the provided device info.
    ####################################################################################################################
    def __init__(self, device):
        self.serial_number = device.serial_number

    ####################################################################################################################
    # Returns an name for the device.
    ####################################################################################################################
    def get_name(self):
        return self.serial_number

    ####################################################################################################################
    # Returns a list of ADBSKADevices. (Actually, it contains all USB devices connected to the computer).
    ####################################################################################################################
    @staticmethod
    def list_devices():
        usb_devices = []
        for device in AdbCommands.Devices():
            usb_devices.append(ADBSKADevice(device))

        return usb_devices

    ####################################################################################################################
    # Connects to the adb daemon on the given device (by serial number).
    ####################################################################################################################
    def connect(self):
        if self.serial_number is None:
            print 'No serial number configured for device.'
            return False

        for device in AdbCommands.Devices():
            if device.serial_number == self.serial_number:
                self.adb_daemon = connect_to_adb_daemon(device)
                if self.adb_daemon is not None:
                    return True
                else:
                    print 'Unable to connect to ADB daemon on device ' + self.serial_number + '.'
                    return False

        print 'Given device ' + self.serial_number + ' not found.'
        return False

    ####################################################################################################################
    # Disconnects from the ADB daemon, and the USB device.
    ####################################################################################################################
    def disconnect(self):
        if self.adb_daemon:
            disconnect_from_adb_daemon(self.adb_daemon)

    ####################################################################################################################
    # Gets simple data through pulling a file with adb.
    # DATA needs to be a dictionary of key-value pairs (the value is not used, only the key).
    ####################################################################################################################
    def get_data(self, data):
        print 'Starting data retrieval service.'
        start_service(self.adb_daemon, OUT_DATA_SERVICE, data)
        time.sleep(2)

        print 'Downloading file with data.'
        try:
            data = self.adb_daemon.Pull(OUT_DATA_REMOTE_FILEPATH)
            return json.loads(data)
        except AdbCommandFailureException, e:
            print 'Could not get data file, file may not exist on device.'

        return []

    ####################################################################################################################
    # Sends simple data through pushing a file with adb.
    # DATA needs to be a dictionary of key-value pairs.
    ####################################################################################################################
    def send_data(self, data):
        # Everything is called "in" since, from the point of view of the Service, it is getting data.
        print 'Starting data receival service.'
        start_service(self.adb_daemon, IN_DATA_SERVICE, data)
        print 'Data sent.'

    ####################################################################################################################
    #
    ####################################################################################################################
    def send_file(self, file_path, file_id):
        print 'Pushing file.'
        self.adb_daemon.Push(file_path, IN_FILE_REMOTE_FILEPATH)

        print 'Starting file receiver service.'
        start_service(self.adb_daemon, IN_FILE_SERVICE, {'file_id': file_id})
        print 'File sent.'

####################################################################################################################
# Test script.
####################################################################################################################
def test():
    devices = ADBSKADevice.list_devices()
    if len(devices) > 0:
        device = devices[0]
        print device
        print device.serial_number

        adbDevice = ADBSKADevice(device)

        try:
            adbDevice.connect()

            print 'Getting id'
            data = adbDevice.get_id()
            print data

            print 'Sending files'
            print 'Files sent'
        finally:
            adbDevice.disconnect()

# Execute the test.
#test()
