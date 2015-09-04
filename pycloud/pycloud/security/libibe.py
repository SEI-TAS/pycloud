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

IBE_GEN_EXECUTABLE = "/usr/local/bin/gen"
IBE_CRYPT_EXECUTABLE = "/usr/local/bin/ibe"
WORKING_FOLDER = "/usr/local/etc"

class LibIBE():
    ##############################################################################################################
    # Runs ibe gen command to create master private key and parameters.
    ##############################################################################################################
    def gen(self, private_key_filepath, public_key_filepath):
        # Set the private key filepath.
        command = "sed -ie s/share/" + private_key_filepath + "/g gen.cnf"
        subprocess.Popen(command, cwd=WORKING_FOLDER)

        # Sets the IBE params file name in the IBE generation config file. This is where the IBE params will be stored.
        command = "sed -ie s/params.txt/" + public_key_filepath + "/g gen.cnf"
        subprocess.Popen(command, cwd=WORKING_FOLDER)

        # Sets the IBE params file in the IBE execution config file. This is so that encryption can find the params.
        command = "sed -ie s/params.txt/" + public_key_filepath + "/g ibe.cnf"
        subprocess.Popen(command, cwd=WORKING_FOLDER)

        # Actually generate the params and master private key.
        subprocess.Popen(IBE_GEN_EXECUTABLE, cwd=WORKING_FOLDER)

    ##############################################################################################################
    # Creates a private key from the given id and master private key ("share"), using the stored IBE params.
    ##############################################################################################################
    def extract(self, id, share):
        privkey = subprocess.check_output([IBE_CRYPT_EXECUTABLE, "extract", id, share], cwd=WORKING_FOLDER)
        return privkey

    ##############################################################################################################
    # Creates a "certificate" hash from the given id and master private key ("share"), using the stored IBE params.
    ##############################################################################################################
    def certify(self, id, share):
        cert = subprocess.check_output([IBE_CRYPT_EXECUTABLE, "certify", id, share], cwd=WORKING_FOLDER)
        return cert
