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

import datetime

from pycloud.pycloud.mongo import Model
from pycloud.pycloud.cloudlet import get_cloudlet_instance
from pycloud.pycloud.security import radius
from pycloud.pycloud.security import credentials
from pycloud.pycloud.model.paired_device import PairedDevice

# ###############################################################################################################
# Represents a deployment of authorization on the cloudlet.
################################################################################################################
class Deployment(Model):
    # Meta class is needed so that minimongo can map this class onto the database.
    class Meta:
        collection = "deployment"
        external = ['_id', 'auth_start', 'auth_duration']
        mapping = {
        }

    ################################################################################################################
    # Constructor.
    ################################################################################################################
    def __init__(self, *args, **kwargs):
        self.auth_start = None
        self.auth_duration = 0
        self.cloudlet = None
        self.radius_server = None
        self.server_keys = None
        super(Deployment, self).__init__(*args, **kwargs)

    ################################################################################################################
    # Set up from configuration stored in cloudlet singleton.
    ################################################################################################################
    def config_setup(self):
        self.cloudlet = get_cloudlet_instance()
        self.radius_server = radius.RadiusServer(self.cloudlet.radius_users_file,
                                                 self.cloudlet.radius_certs_folder,
                                                 self.cloudlet.radius_eap_conf_file)
        self.server_keys = credentials.ServerCredentials.create_object(self.cloudlet.credentials_type,
                                                                       self.cloudlet.data_folder)

    ################################################################################################################
    # Overrides the save method to remove keys we don't want to store temporarily.
    ################################################################################################################
    def save(self, *args, **kwargs):
        self.cloudlet = None
        self.radius_server = None
        self.server_keys = None
        super(Deployment, self).save(*args, **kwargs)

        self.config_setup()

    ################################################################################################################
    # Returns an instance of Depoyment, with data from DB if any, and config already setup.
    ################################################################################################################
    @staticmethod
    def get_instance():
        deployment = Deployment.find_one()
        if not deployment:
            deployment = Deployment()
        deployment.config_setup()
        return deployment

    ############################################################################################################
    # Removes the deployment.
    ############################################################################################################
    def remove(self):
        return Deployment.find_and_modify(query={}, remove=True)

    ############################################################################################################
    # Clears all deployment info.
    ############################################################################################################
    def clear(self):
        # Remove users from RADIUS server.
        print 'Removing paired devices from RADIUS server.'
        devices = PairedDevice.find()
        device_ids = []
        for device in devices:
            device_ids.append(device.device_id)
            device.stop_associated_instance()

        self.radius_server.remove_user_credentials(device_ids)

        # Remove all data from DB.
        print 'Clearing up database.'
        PairedDevice.clear_data()

    ############################################################################################################
    # Bootstraps encryption material and configs.
    ############################################################################################################
    def bootstrap(self, duration):
        self.clear()

        # Create server keys.
        server_keys = credentials.ServerCredentials.create_object(self.cloudlet.credentials_type,
                                                                  self.cloudlet.data_folder)
        server_keys.generate_and_save_to_file()

        # Create RADIUS server certificate.
        self.radius_server.generate_certificate()

        # Set up a new deployment.
        self.auth_start = datetime.datetime.now()
        self.auth_duration = duration
        self.save()

    ################################################################################################################
    # Pairs a connected device to this deployment.
    ################################################################################################################
    def pair_device(self, device_internal_id, connection_id, device_type):
        try:
            # Check if the device was already paired, and if so, abort.
            previously_paired_device = PairedDevice.by_id(device_internal_id)
            if previously_paired_device:
                raise Exception("Device with id {} is already paired.".format(device_internal_id))

            # Generate credentials, register the device, and return them.
            device_keys = self.__generate_device_credentials(device_internal_id)
            self.__register_device(device_internal_id, connection_id, device_keys.auth_password,
                                   device_keys.encryption_password, device_type)

            return device_keys
        except Exception, e:
            raise Exception("Error pairing with device: " + str(e))

    ################################################################################################################
    # Generates the needed credentials for a device being paired.
    ################################################################################################################
    def __generate_device_credentials(self, device_id):
        # Prepare the server and device credential objects.
        device_keys = credentials.DeviceCredentials.create_object(self.cloudlet.credentials_type,
                                                                  self.cloudlet.data_folder,
                                                                  device_id,
                                                                  self.server_keys.private_key_path,
                                                                  self.server_keys.public_key_path,)

        # Create the device's private key and the device's passwords.
        device_keys.generate_and_save_to_file()
        return device_keys

    ############################################################################################################
    # Pair a cloudlet instead of a device
    ############################################################################################################
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


    ############################################################################################################
    # Register a device after pairing it.
    ############################################################################################################
    def __register_device(self, device_id, connection_id, auth_password, enc_password, device_type):
        # Create a new paired device with the id info we just received.
        print 'Adding paired device to DB.'
        paired_device = PairedDevice()
        paired_device.device_id = device_id
        paired_device.connection_id = connection_id
        paired_device.password = enc_password
        paired_device.type = device_type

        # By default, authorization for a device will be the same as the deployment info.
        paired_device.auth_start = self.auth_start
        paired_device.auth_duration = self.auth_duration
        paired_device.auth_enabled = True

        # Store the paired device.
        paired_device.save()

        # Store the new device credentials in the RADIUS server.
        self.radius_server.add_user_credentials(paired_device.device_id, auth_password)

        # Go to the main page.
        print 'Device added to DB.'

    ############################################################################################################
    #
    ############################################################################################################
    def send_paired_credentials(self, curr_device, device_keys):
        # Send the server's public key.
        curr_device.send_file(self.server_keys.public_key_path, 'server_public.key')

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

    ############################################################################################################
    #
    ############################################################################################################
    def clear_device_keys(self, device_keys):
        # Remove the device private key and password files, for security cleanup.
        if device_keys:
            device_keys.delete_key_files()

    ############################################################################################################
    #
    ############################################################################################################
    def unpair_device(self, device_id):
        # Remove it from the list.
        print 'Removing paired device from DB.'
        paired_device = PairedDevice.by_id(device_id)
        paired_device.stop_associated_instance()
        PairedDevice.find_and_remove(device_id)

        # Remove from RADIUS server.
        print 'Removing paired device from RADIUS server.'
        self.radius_server.remove_user_credentials([device_id])

    ############################################################################################################
    #
    ############################################################################################################
    def revoke_device(self, device_id):
        # Mark it as disabled.
        paired_device = PairedDevice.by_id(device_id)
        paired_device.auth_enabled = False
        paired_device.save()
        paired_device.stop_associated_instance()

        # Remove from RADIUS server.
        print 'Removing paired device from RADIUS server.'
        self.radius_server.remove_user_credentials([device_id])

    ############################################################################################################
    #
    ############################################################################################################
    def reauthorize_device(self, device_id):
        # Mark it as enabled.
        paired_device = PairedDevice.by_id(device_id)
        paired_device.auth_enabled = True
        paired_device.save()

        # Store the device credentials in the RADIUS server.
        self.radius_server.add_user_credentials(paired_device.device_id, paired_device.password)
