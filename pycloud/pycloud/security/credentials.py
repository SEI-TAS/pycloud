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
    # Just creates an object, checking that the type is valid.
    ############################################################################################################
    def __init__(self, type, root_folder):
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

        # Build the full paths.
        self.keys_folder = os.path.join(root_folder, LOCAL_FOLDER)
        self.private_key_path = os.path.join(self.keys_folder, SERVER_PRIVATE_KEY_FILE_NAME)
        self.public_key_path = os.path.join(self.keys_folder, SERVER_PUBLIC_KEY_FILE_NAME)

    ############################################################################################################
    # Creates the server keys and saves them to files.
    ############################################################################################################
    def generate_and_save_to_file(self):
        # Ensure the folder is there, and clean it up too.
        fileutils.recreate_folder(self.keys_folder)

        if self.type == "IBE":
            # The IBE lib saves to files when creating the keys.
            ibe = libibe.LibIBE()
            ibe.gen(self.private_key_path, self.public_key_path)

            # Load the keys.
            with open(self.private_key_path, 'r') as keyfile:
                self.private_key = keyfile.read()

            with open(self.public_key_path, 'r') as keyfile:
                self.public_key = keyfile.read()
        elif self.type == "SKE":
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
class DeviceCredentials(object):
    ############################################################################################################
    #
    ############################################################################################################
    def __init__(self, type, root_folder, device_id, server_private_key_path):
        self.id = device_id
        self.type = type

        self.private_key = None
        self.password = None

        # Load the server private key file, which we will need for generation.
        self.server_private_key_file_path = server_private_key_path
        with open(server_private_key_path, 'r') as keyfile:
            self.server_private_key = keyfile.read()

        if self.type == "IBE":
            pass
        elif self.type == "SKE":
            pass
        else:
            raise RuntimeError("The crypter type '{}' is not currently supported.".format(self.type))

        # Build the full paths.
        self.keys_folder = os.path.join(root_folder, LOCAL_FOLDER)
        self.private_key_path = os.path.join(self.keys_folder, DEVICE_PRIVATE_KEY_FILE_NAME)
        self.password_file_path = os.path.join(self.keys_folder, DEVICE_PASSWORD_FILE_NAME)

    ############################################################################################################
    # Creates and stores the credentials.
    ############################################################################################################
    def generate_and_save_to_file(self):
        # Create the keys depending on the type.
        if self.type == "IBE":
            ibe = libibe.LibIBE()
            self.private_key = ibe.extract(self.id, self.server_private_key_file_path)
            self.password = ibe.certify(self.id, self.server_private_key_file_path)
        elif self.type == "SKE":
            self.private_key = self.server_private_key + self.id
            self.password = hashlib.sha256(self.private_key).hexdigest()

        # Store them to files.
        with open(self.private_key_path, 'w') as keyfile:
            keyfile.write(self.private_key)

        with open(self.password_file_path, 'w') as keyfile:
            keyfile.write(self.password)
