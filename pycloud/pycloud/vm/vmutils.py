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

HYPERVISOR_SYSTEM_URI = "qemu:///system"
HYPERVISOR_SESSION_URI = "qemu:///session"

_hypervisor = None


################################################################################################################
# Returns the hypervisor connection and will auto connect if the connection is null
################################################################################################################
def get_hypervisor():
    global _hypervisor
    if _hypervisor is None:
        _hypervisor = libvirt.open(HYPERVISOR_SYSTEM_URI)
    return _hypervisor

################################################################################################################
# Helper to convert normal uuid to string
################################################################################################################
def uuidstr(rawuuid):
    hx = ['0', '1', '2', '3', '4', '5', '6', '7',
          '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
    uuid = []
    for i in range(16):
        uuid.append(hx[((ord(rawuuid[i]) >> 4) & 0xf)])
        uuid.append(hx[(ord(rawuuid[i]) & 0xf)])
        if i == 3 or i == 5 or i == 7 or i == 9:
            uuid.append('-')
    return "".join(uuid)

################################################################################################################
# Will destroy all virtual machines that are running
################################################################################################################
def destroy_all_vms():
    print 'Shutting down all running virtual machines:'
    hypervisor = get_hypervisor()
    vm_ids = hypervisor.listDomainsID()
    for vm_id in vm_ids:
        vm = hypervisor.lookupByID(vm_id)
        print '\tShutting down \'VM-%s\'' % uuidstr(vm.UUID())
        vm.destroy()
    print 'All machines shutdown'
