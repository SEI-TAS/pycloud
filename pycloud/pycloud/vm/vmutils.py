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
# Exception type used in our system.
################################################################################################################
class VirtualMachineException(Exception):
    def __init__(self, message):
        super(VirtualMachineException, self).__init__(message)
        self.message = message


################################################################################################################
#
################################################################################################################
class VirtualMachine(object):

    ################################################################################################################
    #
    ################################################################################################################
    def __init__(self):
        self.vm = None

    ################################################################################################################
    # Returns the hypervisor connection and will auto connect if the connection is null.
    ################################################################################################################
    @staticmethod
    def _get_hypervisor(is_system_level=True):
        global _hypervisor
        if _hypervisor is None:
            _hypervisor = VirtualMachine.connect_to_hypervisor(is_system_level)
        return _hypervisor

    ################################################################################################################
    # Returns the hypervisor connection.
    ################################################################################################################
    @staticmethod
    def connect_to_hypervisor(is_system_level=True, host_name=''):
        try:
            uri = VirtualMachine._get_qemu_libvirt_connection_uri(is_system_level, host_name=host_name)
            hypervisor = libvirt.open(uri)
            return hypervisor
        except libvirt.libvirtError, e:
            raise VirtualMachineException(str(e))

    ################################################################################################################
    # Builds a libvir URI for a QEMU connection.
    ################################################################################################################
    @staticmethod
    def _get_qemu_libvirt_connection_uri(is_system_level=False, host_name=''):
        uri = QEMU_URI_PREFIX + host_name
        if is_system_level:
            uri += SYSTEM_LIBVIRT_DAEMON_SUFFIX
        else:
            uri += SESSION_LIBVIRT_DAEMON_SUFFIX
        return uri

    ################################################################################################################
    # Lookup a specific instance by its uuid
    ################################################################################################################
    def connect_to_virtual_machine(self, uuid):
        try:
            self.vm = VirtualMachine._get_hypervisor().lookupByUUIDString(uuid)
        except libvirt.libvirtError, e:
            raise VirtualMachineException(str(e))

    ################################################################################################################
    # Get the XML description of a running VM.
    ################################################################################################################
    def get_running_vm_xml_string(self):
        try:
            return self.vm.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE)
        except libvirt.libvirtError, e:
            raise VirtualMachineException(str(e))

    ################################################################################################################
    # Get the XML description of a stored VM.
    ################################################################################################################
    @staticmethod
    def get_stored_vm_xml_string(saved_state_filename):
        try:
            return VirtualMachine._get_hypervisor().saveImageGetXMLDesc(saved_state_filename, 0)
        except libvirt.libvirtError, e:
            raise VirtualMachineException(str(e))

    ################################################################################################################
    # Creates and starts a new VM from an XML description.
    ################################################################################################################
    def create_and_start_vm(self, xml_descriptor):
        try:
            self.vm = VirtualMachine._get_hypervisor().createXML(xml_descriptor, 0)
        except libvirt.libvirtError, e:
            raise VirtualMachineException(str(e))

    ################################################################################################################
    # Save the state of the give VM to the indicated file.
    ################################################################################################################
    def save_state(self, vm_state_image_file):
        try:
            # We indicate that we want want to use as much bandwidth as possible to store the VM's memory when suspending.
            unlimited_bandwidth = 1000000
            self.vm.migrateSetMaxSpeed(unlimited_bandwidth, 0)

            result = self.vm.save(vm_state_image_file)
            if result != 0:
                raise VirtualMachineException("Cannot save memory state to file {}".format(vm_state_image_file))
        except libvirt.libvirtError, e:
            raise VirtualMachineException(str(e))

    ################################################################################################################
    #
    ################################################################################################################
    @staticmethod
    def restore_saved_vm(saved_state_filename, updated_xml_descriptor):
        try:
            VirtualMachine._get_hypervisor().restoreFlags(saved_state_filename, updated_xml_descriptor,
                                                          libvirt.VIR_DOMAIN_SAVE_RUNNING)
        except libvirt.libvirtError as e:
            raise VirtualMachineException(str(e))

    ################################################################################################################
    #
    ################################################################################################################
    def pause(self):
        try:
            result = self.vm.suspend()
            was_suspend_successful = result == 0
            return was_suspend_successful
        except libvirt.libvirtError, e:
            raise VirtualMachineException(str(e))

    ################################################################################################################
    #
    ################################################################################################################
    def unpause(self):
        try:
            result = self.vm.resume()
            was_resume_successful = result == 0
            return was_resume_successful
        except libvirt.libvirtError, e:
            raise VirtualMachineException(str(e))

    ################################################################################################################
    #
    ################################################################################################################
    def destroy(self):
        try:
            self.vm.destroy()
        except libvirt.libvirtError, e:
            raise VirtualMachineException(str(e))

    ################################################################################################################
    #
    ################################################################################################################
    def perform_memory_migration(self, remote_host, p2p=True):
        # Prepare basic flags. Bandwidth 0 lets libvirt choose the best value
        # (and some hypervisors do not support it anyway).
        flags = 0
        new_id = None
        bandwidth = 0

        if p2p:
            flags = flags | libvirt.VIR_MIGRATE_PEER2PEER | libvirt.VIR_MIGRATE_TUNNELLED
            uri = None
        else:
            uri = None
            #uri = VirtualMachine._get_qemu_libvirt_connection_uri(is_system_level=True, host_name=remote_host)

        try:
            # Migrate the state and memory (note that have to connect to the system-level libvirtd on the remote host).
            remote_hypervisor = VirtualMachine.connect_to_hypervisor(is_system_level=True, host_name=remote_host)
            self.vm.migrate(remote_hypervisor, flags, new_id, uri, bandwidth)
        except libvirt.libvirtError, e:
            raise VirtualMachineException(str(e))


################################################################################################################
# Helper to convert normal uuid to string
################################################################################################################
def uuid_to_str(raw_uuid):
    hx = ['0', '1', '2', '3', '4', '5', '6', '7',
          '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
    uuid = []
    for i in range(16):
        uuid.append(hx[((ord(raw_uuid[i]) >> 4) & 0xf)])
        uuid.append(hx[(ord(raw_uuid[i]) & 0xf)])
        if i == 3 or i == 5 or i == 7 or i == 9:
            uuid.append('-')
    return "".join(uuid)
