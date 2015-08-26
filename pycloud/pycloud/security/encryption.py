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

from Crypto.Cipher import AES
from Crypto import Random
import hashlib
import base64
import binascii

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s : s[0:-ord(s[-1])]

#################################################################################################################
# Encrypts a message in an AES encrypted base64 string.
#################################################################################################################
def encrypt_message(message, password):
    #print 'Using password: ' + password
    key = hashlib.sha256(password).digest()
    iv = Random.new().read(AES.block_size)
    encryption_suite = AES.new(key, AES.MODE_CBC, IV=iv)
    #print 'IV: ' + binascii.hexlify(bytearray(iv))

    padded = pad(message)
    cipher_text = encryption_suite.encrypt(padded)
    #print 'Cipher Text: ' + binascii.hexlify(bytearray(cipher_text))
    return base64.b64encode(iv + cipher_text)

#################################################################################################################
# Decrypts an AES encrypted base64 string into plain text.
#################################################################################################################
def decrypt_message(message, password):
    #print 'Using password: ' + password
    decoded_message = base64.b64decode(message)

    key = hashlib.sha256(password).digest()
    iv = decoded_message[:16]
    cipher_text = decoded_message[16:]
    #print 'IV: ' + binascii.hexlify(bytearray(iv))
    #print 'Cipher Text: ' + binascii.hexlify(bytearray(cipher_text))
    decryption_suite = AES.new(key, AES.MODE_CBC, IV=iv)

    plain_text = decryption_suite.decrypt(cipher_text)
    unpadded = unpad(plain_text)
    return unpadded

#################################################################################################################
# Test.
#################################################################################################################
def test():
    message = 'hadasd asd asd sdf as sdf ksfdj kjsdk ksjd lkds ghaksfn ksdi'
    password = '12345'
    print message
    crypted = encrypt_message(message, password)
    print crypted
    decrypted = decrypt_message(crypted, password)
    print decrypted
