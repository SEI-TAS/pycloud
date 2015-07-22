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

from OpenSSL import crypto, SSL
from socket import gethostname
import M2Crypto
import os

#############################################################################################
# Creates a key pair and stores it in the given locations.
#############################################################################################
def create_key_pair(private_key_file_path, public_key_file_path):
    # Seed the random number generator with 1024 random bytes (8192 bits)
    M2Crypto.Rand.rand_seed(os.urandom(1024))

    print "Generating a 2048 bit private/public key pair..."
    keypair = M2Crypto.RSA.gen_key(2048, 65537)
    keypair.save_key(private_key_file_path, None)
    keypair.save_pub_key(public_key_file_path)

#############################################################################################
#
#############################################################################################
def create_self_signed_cert(cert_file_path, private_key_file_path):

    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 1024)

    # create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = "USA"
    cert.get_subject().ST = "Cloudlet"
    cert.get_subject().L = "Cloudlet"
    cert.get_subject().O = "Pycloud"
    cert.get_subject().OU = "Pycloud"
    cert.get_subject().CN = gethostname()
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10*365*24*60*60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha1')

    open(cert_file_path, "wt").write(
        crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    open(private_key_file_path, "wt").write(
        crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
