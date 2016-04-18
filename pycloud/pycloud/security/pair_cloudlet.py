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

import datetime

from pycloud.pycloud.mongo import Model, ObjectID
from pycloud.pycloud.cloudlet import get_cloudlet_instance
from pycloud.pycloud.security import radius
from pycloud.pycloud.security import credentials
from pycloud.pycloud.model.paired_device import PairedDevice

class PairCloudlet():

def pair_cloudlet(self, curr_device):
    type = 'cloudlet'
    try:
        # Following line is for testing only
        # curr_device = None
        # Now the pairing process will be followed, generating all required credentials.
        # The first step is to connect to the device.
        successful_connection = curr_device.connect()
        #if not successful_connection:
        #    raise Exception("Could not connect to device with id {}.".format(id))

        # Get the device id.
        id_data = curr_device.get_data({'device_id': 'none'})
        device_internal_id = id_data['device_id']
        print 'Device id: ' + device_internal_id

        # Check if the device was already paired, and if so, abort.
        previously_paired_device = PairedDevice.by_id(device_internal_id)
        if previously_paired_device:
            raise Exception("Device with id {} is already paired.".format(device_internal_id))

        # Prepare the server and device credential objects.
        server_keys = credentials.ServerCredentials.create_object(self.cloudlet.credentials_type,
                                                                  self.cloudlet.data_folder)
        device_keys = credentials.DeviceCredentials.create_object(self.cloudlet.credentials_type,
                                                                  self.cloudlet.data_folder,
                                                                  device_internal_id,
                                                                  server_keys.private_key_path)

        # Create the device's private key and the device's passwords.
        device_keys.generate_and_save_to_file()

        # Send the server's public key.
        curr_device.send_file(server_keys.public_key_path, 'server_public.key')

        # Send the device's private key to the device.
        curr_device.send_file(device_keys.private_key_path, 'device.key')

        # Send RADIUS certificate to the device.
        cert_file_name = radius.RADIUS_CERT_FILE_NAME
        curr_device.send_file(self.radius_server.cert_file_path, cert_file_name)

        # Send a command to create a Wi-Fi profile on the device. The message has to contain three key pairs:
        # ssid, the RADIUS certificate filename, and the password to be used in the profile.
        ssid = self.cloudlet.ssid
        curr_device.send_data({'command': 'wifi-profile', 'ssid': ssid, 'server_cert_name': cert_file_name,
                               'password': device_keys.auth_password})

        # Remove the device private key and password files, for security cleanup.
        device_keys.delete_key_files()

        # Register the device as authorized in the DBses.
        # Temporarily commented out the original version because there is no curr_device for WiFi pairing
        # self.__register_device(device_internal_id, curr_device.get_name(), device_keys.auth_password, device_keys.encryption_password, type)
        self.__register_device(device_internal_id, 'ABCDEFGH', device_keys.auth_password, device_keys.encryption_password, type)
    except Exception, e:
        raise Exception("Error pairing with device: " + str(e))
    finally:
        if curr_device is not None:
            try:
                print 'Closing connection.'
                curr_device.disconnect()
            except Exception, e:
                raise Exception("Error closing connection with device: " + str(e))
