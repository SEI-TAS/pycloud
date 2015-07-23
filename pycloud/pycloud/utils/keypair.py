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

import M2Crypto
import os
import binascii
import base64
import struct

DEFAULT_RSA_LENGTH_BITS = 2048
DEFAULT_RSA_PUB_EXPONENT = 65537

#############################################################################################
# Creates a key pair and stores it in the given locations.
#############################################################################################
def create_key_pair(private_key_file_path, public_key_file_path, key_length=DEFAULT_RSA_LENGTH_BITS, exponent=DEFAULT_RSA_PUB_EXPONENT):
    # Seed the random number generator with 1024 random bytes (8192 bits)
    M2Crypto.Rand.rand_seed(os.urandom(1024))

    print "Generating a 2048 bit private/public key pair..."
    keypair = M2Crypto.RSA.gen_key(key_length, exponent)
    keypair.save_key(private_key_file_path, None)
    keypair.save_pub_key(public_key_file_path)

    print "Public exponent: " + str(get_exponent(keypair))
    print "Modulus: " + str(get_modulus(keypair))

#############################################################################################
# Returns the exponent as an int, assuming its size in bytes is written in 1 byte.
#############################################################################################
def get_exponent(keypair):
    return get_int_from_der(keypair.e, 1)

#############################################################################################
# Returns the modulus, asuming it is key whose length in bytes is written in 2 bytes.
# The extra one removed is the 00 added to pad).
#############################################################################################
def get_modulus(keypair):
    return get_int_from_der(keypair.n, 3)

#############################################################################################
# Converts a public RSA key from PEM format into adbkey.pub format.
# NOTE: this assumes that the ASB keys are all of 2048-bit length.
#############################################################################################
def convert_pub_rsa_to_adb(rsa_file_path, adb_file_path):
    print "Converting RSA public key file into adbkey.pub..."

    # Get values from the RSA public key.
    public_key = M2Crypto.RSA.load_pub_key(rsa_file_path)
    exponent = get_exponent(public_key)
    modulus = get_modulus(public_key)

    key_size_bits = DEFAULT_RSA_LENGTH_BITS

    # Calculate derived values.
    length = key_size_bits / 32 # Key size in words (4-byte chunks)
    r = pow(2, key_size_bits)
    rr = pow(r, 2) % modulus
    #print 'R: ' + str(pow(2, key_size_bits))
    print 'RR: ' + hex(rr)

    # Transform length and exponent into byte arrays.
    length_array = int_to_bytes(length, endianness='little')
    exponent_array = int_to_bytes(exponent, endianness='little')
    #print 'Exp: ' + binascii.hexlify(exponent_array)

    # Move big integers into arrays.
    modulus_array = int_to_bytes(modulus, endianness='little')
    rr_array = int_to_bytes(rr, endianness='little')
    print 'Mod Array: ' + binascii.hexlify(modulus_array)
    print 'RR Array: ' + binascii.hexlify(rr_array)

    # Calculate remaining values.
    b = pow(2, 32)
    n0inv = b - mod_inverse(modulus, b)
    n0inv_array = int_to_bytes(n0inv, endianness='little')

    # Put all values in one byte array.
    data = length_array + n0inv_array + modulus_array + rr_array + exponent_array
    print 'Total size: ' + str(len(data))

    # Base64 encode the whole thing.
    b64_string = base64.b64encode(data)

    # Add the unused user.
    key_string = b64_string + ' unknown@unknown'

    # Store into file.
    with open(adb_file_path, "w") as text_file:
        text_file.write(key_string)

#############################################################################################
# Returns an integer from a DER value (which comes with its overhead/length).
#############################################################################################
def get_int_from_der(der_value, bytes_to_remove=0):
    # Remove leading 0s, but ensure we have a valid hex representation (it may need 1 leading zero).
    hex = binascii.hexlify(der_value)
    stripped_hex = hex.lstrip('0')
    if len(stripped_hex) % 2 != 0:
        stripped_hex = '0' + stripped_hex

    #print stripped_hex

    # Remove the overhead (usually length).
    value_hex = stripped_hex[2*bytes_to_remove:]

    #print value_hex

    # Return the int representation of this hex value.
    return int(value_hex, 16)

###################################################################################
#
###################################################################################
def int_to_bytes(val, endianness='big'):
    print 'Original value: ' + hex(val)

    # Define endianness for each byte.
    if endianness == 'big':
        prefix = '>'
    else:
        prefix = '<'

    # Check how many 4-byte words we will need.
    four_byte_mask = pow(2, 32) - 1
    num_words = 0
    val_check = val
    parts = []
    while val_check != 0:
        # "Cut" the part we are currently getting.
        current_lower_part = val_check & four_byte_mask
        #print 'Total: ' + hex(val_check)
        #print 'Current: ' + hex(current_lower_part)
        parts.append(current_lower_part)
        val_check >>= 32
        num_words += 1

    # The minimum is 1 word, even for a 0 as a value.
    if num_words == 0:
        num_words = 1
        parts = [val]

    # By default, the array parts will be little-endian, since we put the smaller pieces first.
    if endianness == 'big':
        parts = parts[::-1]

    print 'Num words: ' + str(num_words)

    struct_def = struct.Struct(prefix + 'I'*num_words)
    data = struct_def.pack(*parts)
    #print str(val) + ' Packed: ' + binascii.hexlify(data) +
    print 'Size ' + str(struct_def.size)

    return bytearray(data)

###################################################################################
#
###################################################################################
def mod_inverse(x, p):

    """
    Calculate the modular inverse of x ( mod p )
    the modular inverse is a number such that:
    (inverse(x, p) * x) % p == 1
    you could think of this as: 1/x
    """
    inv1 = 1
    inv2 = 0
    while p != 1 and p != 0:
        inv1, inv2 = inv2, inv1 - inv2 * (x / p)
        x, p = p, x % p

    return inv2

# Test
create_key_pair('./test', './test2')
convert_pub_rsa_to_adb('./test2', './adbkey_test.pub')
