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

# Python wrappers for Stanford IBE library

import subprocess
import os

from pycloud.pycloud.utils.fileutils import replace_in_file

IBE_GEN_EXECUTABLE = "/usr/local/bin/gen"
IBE_CRYPT_EXECUTABLE = "/usr/local/bin/ibe"
IBE_CONFIG_FILES_FOLDER = "/usr/local/etc/ibe/"

IBE_GEN_CONFIG_FILE = os.path.join(IBE_CONFIG_FILES_FOLDER, 'gen.cnf')
IBE_CRYPT_CONFIG_FILE = os.path.join(IBE_CONFIG_FILES_FOLDER, 'ibe.cnf')

##############################################################################################################
# Encapsulates IBE access.
##############################################################################################################
class LibIBE(object):
    ##############################################################################################################
    # Sets a param in a config file.
    ##############################################################################################################
    def set_config_param(self, param, value, config_file_path):
        replace_in_file(r'^' + param + ' = .*$', param + ' = ' + value, config_file_path)

    ##############################################################################################################
    # Runs ibe gen command to create master private key and parameters.
    ##############################################################################################################
    def gen(self, private_key_file_path, public_key_file_path):
        # Set the private key filepath.
        self.set_config_param('sharefiles', private_key_file_path, IBE_GEN_CONFIG_FILE)

        # Sets the IBE params file name in the IBE generation config file. This is where the IBE params will be stored.
        self.set_config_param('params', public_key_file_path, IBE_GEN_CONFIG_FILE)

        # Sets the IBE params file in the IBE execution config file. This is so that encryption can find the params.
        self.set_config_param('params', public_key_file_path, IBE_CRYPT_CONFIG_FILE)

        # Actually generate the params and master private key.
        subprocess.call(IBE_GEN_EXECUTABLE, cwd=IBE_CONFIG_FILES_FOLDER)

    ##############################################################################################################
    # Creates a private key from the given id and master private key ("share"), using the stored IBE params.
    ##############################################################################################################
    def extract(self, id, master_key_file, device_private_key_filepath):
        # Sets the output file for the device key in the config file.
        self.set_config_param('keyfile', device_private_key_filepath, IBE_CRYPT_CONFIG_FILE)

        privkey = subprocess.check_output([IBE_CRYPT_EXECUTABLE, "extract", id, master_key_file], cwd=IBE_CONFIG_FILES_FOLDER)
        return privkey

    ##############################################################################################################
    # Creates a "certificate" hash from the given id and master private key ("share"), using the stored IBE params.
    ##############################################################################################################
    def certify(self, id, master_key_file):
        cert = subprocess.check_output([IBE_CRYPT_EXECUTABLE, "certify", id, master_key_file], cwd=IBE_CONFIG_FILES_FOLDER)
        return cert
