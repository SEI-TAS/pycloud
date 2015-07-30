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

from socket import gethostname
from M2Crypto import X509, RSA, ASN1, EVP
import time

import rsa

# Standard times to be used for any certificate: valid from now to 10 more years.
t = long(time.time()) + time.timezone
before = ASN1.ASN1_UTCTIME()
before.set_time(t)
after = ASN1.ASN1_UTCTIME()
after.set_time(t + 60 * 60 * 24 * 365 * 10) # 10 years

#############################################################################################
#
#############################################################################################
def create_self_signed_cert(cert_file_path, private_key_file_path):
    cert = X509.X509()
    cert.set_version(2)

    # Create subject info.
    cert.get_subject().C = "USA"
    cert.get_subject().ST = "Cloudlet"
    cert.get_subject().L = "Cloudlet"
    cert.get_subject().O = "Pycloud"
    cert.get_subject().OU = "Pycloud"
    cert.get_subject().CN = gethostname()

    # Create secondary params.
    cert.set_serial_number(1000)
    cert.set_not_before(before)
    cert.set_not_after(after)

    # It is self-signed (meaning it is also a CA).
    cert.set_issuer(cert.get_subject())
    ext = X509.new_extension('basicConstraints', 'CA:TRUE')
    cert.add_ext(ext)

    # Generate an RSA key pair, store it in files, and load it.
    rsa.create_key_pair(private_key_file_path, private_key_file_path + ".pub")
    public_key = RSA.load_pub_key(private_key_file_path + ".pub")
    private_key = RSA.load_key(private_key_file_path)

    # Associate the public key we just generated.
    request_public_key = EVP.PKey()
    request_public_key.assign_rsa(public_key)
    cert.set_pubkey(request_public_key)

    # Sign the certificate.
    request_private_key = EVP.PKey()
    request_private_key.assign_rsa(private_key)
    cert.sign(request_private_key, 'sha256')

    # Store the certificate.
    cert.save(cert_file_path)

# Test
#create_self_signed_cert('./cert.pem', './key.rsa')
