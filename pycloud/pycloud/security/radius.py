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
import subprocess

from pycloud.pycloud.security import pki
from pycloud.pycloud.utils import fileutils

RADIUS_CERT_FILE_NAME = 'radius_cert.pem'
RADIUS_PRIVATE_KEY_FILE_NAME = 'radius_private_key'

# User file for FreeRADIUS.
DEFAULT_USERS_FILE_PATH = './data/users'

# Folder to store and retrieve files.
DEFAULT_CERT_STORE_FOLDER = './data/credentials'

# FreeRADIUS EAP config file.
DEFAULT_EAP_CONF_FILE = ''

# Command to restart.
RESTART_COMMAND = "sudo service freeradius restart"

####################################################################################################################
# Class that represents the Radius server interface.
####################################################################################################################
class RadiusServer(object):
    ####################################################################################################################
    # Sets up folders and paths.
    ####################################################################################################################
    def __init__(self, config_users_file_path, config_cert_store_folder, config_eap_file):
        if config_users_file_path is not None:
            self.users_file_path = config_users_file_path
        else:
            self.users_file_path = DEFAULT_USERS_FILE_PATH

        if config_cert_store_folder is not None:
            self.cert_store_folder = config_cert_store_folder
        else:
            self.cert_store_folder = DEFAULT_CERT_STORE_FOLDER

        if config_eap_file is not None:
            self.eap_conf_file = config_eap_file
        else:
            self.eap_conf_file = DEFAULT_EAP_CONF_FILE

        self.cert_file_path = os.path.join(self.cert_store_folder, RADIUS_CERT_FILE_NAME)
        self.private_key_path = os.path.join(self.cert_store_folder, RADIUS_PRIVATE_KEY_FILE_NAME)

    ####################################################################################################################
    # Sets up a new RADIUS certificate and its keys.
    ####################################################################################################################
    def generate_certificate(self):
        fileutils.create_folder_if_new(self.cert_store_folder)
        pki.create_self_signed_cert(self.cert_file_path, self.private_key_path)

        # Configure FreeRADIUS to use the certificate we just created.
        # TODO

    ####################################################################################################################
    # Restarts the server.
    ####################################################################################################################
    def restart(self):
        subprocess.Popen(RESTART_COMMAND)

    ####################################################################################################################
    # Stores user credentials into a RADIUS server. This method works for FreeRADIUS servers.
    ####################################################################################################################
    def add_user_credentials(self, user_id, password):
        user_entry = user_id + '\tCleartext-Password := "' + password + '"' + '\n'
        with open(self.users_file_path, 'a') as users_file:
            users_file.write(user_entry)

    ####################################################################################################################
    # Removes a specific list of users from the users list.
    ####################################################################################################################
    def remove_user_credentials(self, user_ids):
        # First get all lines.
        with open(self.users_file_path, 'r') as users_file:
            file_lines = users_file.readlines()

        # Now rewrite all lines, minus the user we want to remove.
        with open(self.users_file_path, 'w') as users_file:
            for line in file_lines:
                potential_id = line.split('\t')[0]
                #print potential_id + '.'
                if not potential_id in user_ids:
                    users_file.write(line)
