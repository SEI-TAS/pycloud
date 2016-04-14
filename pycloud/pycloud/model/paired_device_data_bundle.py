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


################################################################################################################
#
################################################################################################################
class PairedDeviceDataBundle(object):

    ################################################################################################################
    # Constructor.
    ################################################################################################################
    def __init__(self, *args, **kwargs):
        self.cloudlet_name = None
        self.cloudlet_fqdn = None
        self.cloudlet_port = None
        self.cloudlet_encryption_enabled = False
        self.ssid = None
        self.auth_password = None
        self.server_radius_cert = None
        self.server_public_key = None
        self.device_private_key = None

    ################################################################################################################
    #
    ################################################################################################################
    def fill_from_dict(self, values_dict):
        for key in values_dict:
            setattr(self, key, values_dict[key])

    ################################################################################################################
    # Loads a file.
    ################################################################################################################
    def load_certificate(self, file_path):
        with open(file_path, 'r') as input_file:
            self.server_radius_cert = input_file.read()
