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

import os

from pycloud.pycloud.utils import pki

RADIUS_CERT_FILE_NAME = 'radius_cert.pem'
RADIUS_PRIVATE_KEY_FILE_NAME = 'radius_private_key'

# User file for FreeRADIUS.
USERS_FILE_PATH = '/usr/local/etc/raddb/users'

# Folder to store and retrieve files.
CERT_STORE_FOLDER = '/etc/raddb/certs'

######################################################################################################################
# Returns the full path for the RADIUS certificate.
######################################################################################################################
def get_radius_cert_path():
    return os.path.join(CERT_STORE_FOLDER, RADIUS_CERT_FILE_NAME)

####################################################################################################################
# Sets up a new RADIUS certificate and its keys.
####################################################################################################################
def generate_certificate():
    radius_cert_path = get_radius_cert_path()
    radius_private_key_path = os.path.join(CERT_STORE_FOLDER, RADIUS_PRIVATE_KEY_FILE_NAME)
    pki.create_self_signed_cert(radius_cert_path, radius_private_key_path)

####################################################################################################################
# Stores user credentials into a RADIUS server. This method works for FreeRADIUS servers.
####################################################################################################################
def store_freeradius_user_credentials(user_id, password):
    user_entry = user_id + '\tCleartext-Password := "' + password + '"'
    with open(USERS_FILE_PATH, 'a') as users_file:
        users_file.write(user_entry)
