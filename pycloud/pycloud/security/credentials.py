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
import binascii
import hashlib

import libibe
from pycloud.pycloud.utils import fileutils

LOCAL_FOLDER = 'credentials/'

SERVER_PRIVATE_KEY_FILE_NAME = 'server_private_key'
SERVER_PUBLIC_KEY_FILE_NAME = 'server_public_key'

DEVICE_PRIVATE_KEY_FILE_NAME = 'temp_device_private_key'
DEVICE_PASSWORD_FILE_NAME = 'temp_device_password'

############################################################################################################
#
############################################################################################################
class ServerCredentials(object):
    ############################################################################################################
    # Factory method to create the corresponding server credentials object.
    ############################################################################################################
    @staticmethod
    def create_object(type, root_folder):
        if type == "SKE":
            credentials_object = SKEServerCredentials(root_folder)
        elif type == "IBE":
            credentials_object = IBEServerCredentials(root_folder)
        else:
            raise RuntimeError("The crypter type '{}' is not currently supported.".format(type))

        return credentials_object

    ############################################################################################################
    # Just creates an the object, setting up paths.
    ############################################################################################################
    def __init__(self, root_folder):
        self.private_key_ascii = None
        self.private_key = None
        self.public_key = None

        # Build the full paths.
        self.keys_folder = os.path.join(root_folder, LOCAL_FOLDER)
        self.private_key_path = os.path.join(self.keys_folder, SERVER_PRIVATE_KEY_FILE_NAME)
        self.public_key_path = os.path.join(self.keys_folder, SERVER_PUBLIC_KEY_FILE_NAME)

############################################################################################################
#
############################################################################################################
class SKEServerCredentials(ServerCredentials):
    ############################################################################################################
    # Creates the server keys and saves them to files.
    ############################################################################################################
    def generate_and_save_to_file(self):
        # Ensure the folder is there, and clean it up too.
        fileutils.recreate_folder(self.keys_folder)

        # First create the keys.
        random_number = os.urandom(256)
        self.private_key_ascii = binascii.hexlify(random_number)
        self.private_key = self.private_key_ascii.decode("ascii")
        self.public_key = ""

        # Store the keys.
        with open(self.private_key_path, 'w') as keyfile:
            keyfile.write(self.private_key)

        with open(self.public_key_path, 'w') as keyfile:
            keyfile.write(self.public_key)

############################################################################################################
#
############################################################################################################
class IBEServerCredentials(ServerCredentials):
    ############################################################################################################
    # Creates the server keys and saves them to files.
    ############################################################################################################
    def generate_and_save_to_file(self):
        # Ensure the folder is there, and clean it up too.
        fileutils.recreate_folder(self.keys_folder)

        # The IBE lib saves to files when creating the keys.
        ibe = libibe.LibIBE()
        ibe.gen(self.private_key_path, self.public_key_path)

        # Load the keys.
        with open(self.private_key_path, 'r') as keyfile:
            self.private_key = keyfile.read()

        with open(self.public_key_path, 'r') as keyfile:
            self.public_key = keyfile.read()

############################################################################################################
#
############################################################################################################
class DeviceCredentials(object):
    ############################################################################################################
    # Factory method to create the corresponding server credentials object.
    ############################################################################################################
    @staticmethod
    def create_object(type, root_folder, device_id, server_private_key_path):
        if type == "SKE":
            credentials_object = SKEDeviceCredentials(root_folder, device_id, server_private_key_path)
        elif type == "IBE":
            credentials_object = IBEDeviceCredentials(root_folder, device_id, server_private_key_path)
        else:
            raise RuntimeError("The crypter type '{}' is not currently supported.".format(type))

        return credentials_object

    ############################################################################################################
    #
    ############################################################################################################
    def __init__(self, root_folder, device_id, server_private_key_path):
        self.id = device_id
        self.private_key = None
        self.auth_password = None
        self.encryption_password = None

        # Load the server private key file, which we will need for generation.
        self.server_private_key_file_path = server_private_key_path
        with open(server_private_key_path, 'r') as keyfile:
            self.server_private_key = keyfile.read()

        # Build the full paths.
        self.keys_folder = os.path.join(root_folder, LOCAL_FOLDER)
        self.private_key_path = os.path.join(self.keys_folder, DEVICE_PRIVATE_KEY_FILE_NAME)
        self.encryption_password_file_path = os.path.join(self.keys_folder, DEVICE_PASSWORD_FILE_NAME)

    ############################################################################################################
    #
    ############################################################################################################
    def store_encryption_password(self):
        with open(self.encryption_password_file_path, 'w') as keyfile:
            keyfile.write(self.encryption_password)

    ############################################################################################################
    # Deletes the private key file and the encryption password file.
    ############################################################################################################
    def delete_key_files(self):
        if os.path.exists(self.private_key_path):
            os.remove(self.private_key_path)

        if os.path.exists(self.encryption_password_file_path):
            os.remove(self.encryption_password_file_path)

############################################################################################################
#
############################################################################################################
class SKEDeviceCredentials(DeviceCredentials):
    ############################################################################################################
    # Creates and stores the credentials.
    ############################################################################################################
    def generate_and_save_to_file(self):
        self.private_key = self.server_private_key + self.id
        self.auth_password = hashlib.sha256(self.private_key).hexdigest()
        self.encryption_password = hashlib.sha256(self.private_key[::-1]).hexdigest()

        # Store the private key.
        with open(self.private_key_path, 'w') as keyfile:
            keyfile.write(self.private_key)

        # Store the encryption password.
        self.store_encryption_password()

############################################################################################################
#
############################################################################################################
class IBEDeviceCredentials(DeviceCredentials):
    ############################################################################################################
    # Creates and stores the credentials.
    ############################################################################################################
    def generate_and_save_to_file(self):
        ibe = libibe.LibIBE()
        # IBE generates and stores the private key.
        self.private_key = ibe.extract(self.id, self.server_private_key_file_path, self.private_key_path)

        # IBE generates but doesn't store the cert/password. We remove spaces and convert to lowercase to have a
        # more standardized password.
        ibe_password = ibe.certify(self.id, self.server_private_key_file_path).replace(' ', '').lower()

        # Now truncate it since it is too big for RADIUS, by calculating the 256 SHA hash.
        self.auth_password = hashlib.sha256(ibe_password).hexdigest()

        # Create the encryption password from the ibe password as well.
        self.encryption_password = hashlib.sha256(ibe_password[::-1]).hexdigest()

        # Store the encryption password.
        self.store_encryption_password()
