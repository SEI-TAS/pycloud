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

import radius

############################################################################################################
#
############################################################################################################
class ServerCredentials(object):
    ############################################################################################################
    #
    ############################################################################################################
    def __init__(self, type):
        self.type = type
        if self.type == "IBE":
            raise RuntimeError("IBE is not yet implemented")
        elif self.type == "SKE":
            random_number = os.urandom(256)
            self.server_key_ascii = binascii.hexlify(random_number)
            self.server_key = self.server_key_ascii.decode("ascii")
            self.ServerPub = ""
        else:
            raise RuntimeError("That crypter type is not currently supported.")

    ############################################################################################################
    #
    ############################################################################################################
    def save_to_file(self, args):
        if self.type == "IBE":
            raise RuntimeError("IBE is not yet implemented")
        elif self.type == "SKE":
            with open(args[0], 'w') as keyfile:
                keyfile.write(self.server_key)

############################################################################################################
#
############################################################################################################
class DeviceCredentials(object):
    ############################################################################################################
    #
    ############################################################################################################
    def __init__(self, type, args):
        self.type = type
        with open(args[0], 'r') as keyfile:
            self.server_key = keyfile.read()

        if self.type == "IBE":
            raise RuntimeError("IBE is not yet implemented")
        elif self.type == "SKE":
            self.device_id = args[1]
            self.device_private_key = self.server_key + self.device_id
            self.device_hash = hashlib.sha256(self.device_private_key).hexdigest()
        else:
            raise RuntimeError("That crypter type is not currently supported.")

    ############################################################################################################
    #
    ############################################################################################################
    def save_to_file(self, args):
        if self.type == "IBE":
            raise RuntimeError("IBE is not yet implemented")
        elif self.type == "SKE":
            with open(args[0], 'w') as keyfile:
                keyfile.write(self.device_private_key)

    ############################################################################################################
    #
    ############################################################################################################
    def insert_into_radius(self):
        radius.store_freeradius_user_credentials(self.device_id, self.device_hash)
