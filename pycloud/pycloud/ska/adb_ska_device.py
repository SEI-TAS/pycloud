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

from adb.usb_exceptions import AdbCommandFailureException
from adb.adb_commands import AdbCommands, M2CryptoSigner

from ska_device_interface import ISKADevice

DEVICE_FOLDER = '/sdcard/cloudlet/adb/'

GET_ID_SERVICE = 'edu.cmu.sei.cloudlet.client/.ska.adb.SaveIdToFileService'
GET_ID_FILE = DEVICE_FOLDER + 'id.txt'

LOCAL_CERT_FILE = 'test.txt'
STORE_CERT_SERVICE = 'edu.cmu.sei.cloudlet.client/.ska.adb.StoreCertificateService'
SERVER_CERT_FILE = DEVICE_FOLDER + 'server_certificate.cer'

LOCAL_MKEY_FILE = 'test.txt'
STORE_MKEY_SERVICE = 'edu.cmu.sei.cloudlet.client/.ska.adb.StoreMasterKeyService'
MASTER_KEY_FILE = DEVICE_FOLDER + 'master_key.txt'

LOCAL_PKEY_FILE = 'test.txt'
STORE_PKEY_SERVICE = 'edu.cmu.sei.cloudlet.client/.ska.adb.StoreDeviceKeyService'
DEVICE_PKEY_FILE = DEVICE_FOLDER + 'device_pkey.txt'

######################################################################################################################
# Attempts to connect to an ADB daemon on a given USB device. Returns a proxy to that daemon if succesful, or None if
# unsuccessful
######################################################################################################################
def connect_to_adb_daemon(device):
    # Load host keypair to authenticate with ADB deamon.
    keySigner = M2CryptoSigner('adbkey')

    try:
        print 'Connecting to USB device'
        device.Open()

        print 'Connecting to ADB daemon'
        adbDaemon = AdbCommands.Connect(device, banner="cloudlet", rsa_keys=[keySigner])
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
def start_service(adbDaemon, service_name):
    adbDaemon.Shell('am startservice --user 0 ' + service_name, timeout_ms=20000)

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
    # Gets a device id through pulling a file with adbd.
    ####################################################################################################################
    def get_id(self):
        print 'Starting ID service.'
        start_service(self.adb_daemon, GET_ID_SERVICE)
        time.sleep(2)

        print 'Downloading ID file.'
        try:
            device_id = self.adb_daemon.Pull(GET_ID_FILE)
            return device_id
        except AdbCommandFailureException, e:
            print 'Could not get id file, file may not exist on device.'

        return None

    ####################################################################################################################
    #
    ####################################################################################################################
    def send_server_certificate(self, file_path):
        self.adb_daemon.Push(file_path, SERVER_CERT_FILE)
        start_service(self.adb_daemon, STORE_CERT_SERVICE)
        print 'File sent.'

    ####################################################################################################################
    #
    ####################################################################################################################
    def send_master_public_key(self, file_path):
        self.adb_daemon.Push(file_path, MASTER_KEY_FILE)
        start_service(self.adb_daemon, STORE_MKEY_SERVICE)
        print 'File sent.'

    ####################################################################################################################
    #
    ####################################################################################################################
    def send_device_private_key(self, file_path):
        self.adb_daemon.Push(file_path, DEVICE_PKEY_FILE)
        start_service(self.adb_daemon, STORE_PKEY_SERVICE)
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
            adbDevice.send_server_certificate(LOCAL_CERT_FILE)
            adbDevice.send_master_public_key(LOCAL_MKEY_FILE)
            adbDevice.send_device_private_key(LOCAL_PKEY_FILE)
            print 'Files sent'
        finally:
            adbDevice.disconnect()

# Execute the test.
#test()
