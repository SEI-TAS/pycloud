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

from libibe import LibIBE
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
    # Just creates an object, checking that the type is valid.
    ############################################################################################################
    def __init__(self, type):
        self.type = type

        self.private_key_ascii = None
        self.private_key = None
        self.public_key = None

        if self.type == "IBE":
            pass
        elif self.type == "SKE":
            pass
        else:
            raise RuntimeError("The crypter type '{}' is not currently supported.".format(self.type))

    ############################################################################################################
    # Creates the server keys and saves them to files.
    ############################################################################################################
    def generate_and_save_to_file(self, root_folder):
        # Ensure the folder is there, and clean it up too.
        key_folder = os.path.join(root_folder, LOCAL_FOLDER)
        fileutils.recreate_folder(key_folder)

        # Build the full paths.
        private_key_path = ServerCredentials.get_private_key_file_path(root_folder)
        public_key_path = ServerCredentials.get_public_key_file_path(root_folder)

        if self.type == "IBE":
            # The IBE lib saves to files when creating the keys.
            ibe = LibIBE()
            ibe.gen(private_key_path, public_key_path)
        elif self.type == "SKE":
            # First create the keys.
            random_number = os.urandom(256)
            self.private_key_ascii = binascii.hexlify(random_number)
            self.private_key = self.private_key_ascii.decode("ascii")
            self.public_key = ""

            # Store the keys.
            with open(private_key_path, 'w') as keyfile:
                keyfile.write(self.private_key)

            with open(public_key_path, 'w') as keyfile:
                keyfile.write(self.public_key)

    ############################################################################################################
    #
    ############################################################################################################
    @staticmethod
    def get_private_key_file_path(root_folder):
        path = os.path.join(root_folder, LOCAL_FOLDER, SERVER_PRIVATE_KEY_FILE_NAME)
        return path

    ############################################################################################################
    #
    ############################################################################################################
    @staticmethod
    def get_public_key_file_path(root_folder):
        path = os.path.join(root_folder, LOCAL_FOLDER, SERVER_PUBLIC_KEY_FILE_NAME)
        return path

############################################################################################################
#
############################################################################################################
class DeviceCredentials(object):
    ############################################################################################################
    #
    ############################################################################################################
    def __init__(self, type, device_id, server_private_key_path):
        self.id = device_id
        self.type = type

        self.private_key = None
        self.password = None

        # Load the server private key file, which we will need for generation.
        with open(server_private_key_path, 'r') as keyfile:
            self.server_private_key = keyfile.read()

        if self.type == "IBE":
            pass
        elif self.type == "SKE":
            pass
        else:
            raise RuntimeError("The crypter type '{}' is not currently supported.".format(self.type))

    ############################################################################################################
    # Creates the credentials.
    ############################################################################################################
    def generate(self):
        # Create the keys depending on the type.
        if self.type == "IBE":
            ibe = LibIBE()
            self.private_key = ibe.extract(self.id, self.server_private_key)
            self.password = ibe.certify(self.id, self.server_private_key)
        elif self.type == "SKE":
            self.private_key = self.server_private_key + self.id
            self.password = hashlib.sha256(self.private_key).hexdigest()

    ############################################################################################################
    #
    ############################################################################################################
    def save_to_file(self, root_folder):
        path = DeviceCredentials.get_private_key_file_path(root_folder)
        with open(path, 'w') as keyfile:
            keyfile.write(self.private_key)

        path = DeviceCredentials.get_password_file_path(root_folder)
        with open(path, 'w') as keyfile:
            keyfile.write(self.password)

    ############################################################################################################
    #
    ############################################################################################################
    @staticmethod
    def get_private_key_file_path(root_folder):
        path = os.path.join(root_folder, LOCAL_FOLDER, DEVICE_PRIVATE_KEY_FILE_NAME)
        return path

    ############################################################################################################
    #
    ############################################################################################################
    @staticmethod
    def get_password_file_path(root_folder):
        path = os.path.join(root_folder, LOCAL_FOLDER, DEVICE_PASSWORD_FILE_NAME)
        return path
