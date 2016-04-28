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

__author__ = 'jdroot'

import libvirt

QEMU_URI_PREFIX = "qemu://"
SYSTEM_LIBVIRT_DAEMON_SUFFIX = "/system"
SESSION_LIBVIRT_DAEMON_SUFFIX = "/session"

# Global connection object, only open connection to local hypervisor used by app.
_hypervisor = None

################################################################################################################
# Builds a libvir URI for a QEMU connection.
################################################################################################################
def get_qemu_libvirt_connection_uri(isSystemLevel=False, host_name=''):
    uri = QEMU_URI_PREFIX + host_name
    if isSystemLevel:
        uri += SYSTEM_LIBVIRT_DAEMON_SUFFIX
    else:
        uri += SESSION_LIBVIRT_DAEMON_SUFFIX
    return uri


################################################################################################################
# Returns the hypervisor connection and will auto connect if the connection is null.
################################################################################################################
def get_hypervisor(isSystemLevel=False):
    global _hypervisor
    if _hypervisor is None:
        uri = get_qemu_libvirt_connection_uri(isSystemLevel, host_name='')
        _hypervisor = libvirt.open(uri)
    return _hypervisor


################################################################################################################
# Helper to convert normal uuid to string
################################################################################################################
def uuidstr(raw_uuid):
    hx = ['0', '1', '2', '3', '4', '5', '6', '7',
          '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
    uuid = []
    for i in range(16):
        uuid.append(hx[((ord(raw_uuid[i]) >> 4) & 0xf)])
        uuid.append(hx[(ord(raw_uuid[i]) & 0xf)])
        if i == 3 or i == 5 or i == 7 or i == 9:
            uuid.append('-')
    return "".join(uuid)
