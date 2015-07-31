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

from pycloud.pycloud.utils import fileutils
from pycloud.pycloud.utils import pki

LOCAL_TEMP_FOLDER = 'radius/'

RADIUS_CERT_FILE_NAME = 'radius_cert.pem'
RADIUS_PRIVATE_KEY_FILE_NAME = 'radius_private_key'

# Folder to store and retrieve files.
radius_data_folder = './'

######################################################################################################################
# Returns the full path for the RADIUS certificate.
######################################################################################################################
def get_radius_cert_path():
    return os.path.join(radius_data_folder, RADIUS_CERT_FILE_NAME)

####################################################################################################################
# Sets up a new RADIUS certificate and its keys.
####################################################################################################################
def generate_certificate(new_data_folder):
    global radius_data_folder

    # Set the data folder.
    radius_data_folder = os.path.join(os.path.abspath(new_data_folder), LOCAL_TEMP_FOLDER)
    fileutils.recreate_folder(radius_data_folder)

    # Generate the cert.
    radius_cert_path = os.path.join(radius_data_folder, RADIUS_CERT_FILE_NAME)
    radius_private_key_path = os.path.join(radius_data_folder, RADIUS_PRIVATE_KEY_FILE_NAME)
    pki.create_self_signed_cert(radius_cert_path, radius_private_key_path)