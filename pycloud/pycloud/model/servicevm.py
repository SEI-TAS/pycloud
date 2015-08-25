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

# Import libvirt to access the virtualization API.
import libvirt

import re
import time
import os

# Used to generate unique IDs for the VMs.
from uuid import uuid4

from pycloud.pycloud.utils.netutils import generate_random_mac, find_ip_for_mac, is_port_open, get_adapter_ip_address

from pycloud.pycloud.mongo import Model
from pycloud.pycloud.model.vmimage import VMImage
from pycloud.pycloud.vm.vmsavedstate import VMSavedState
from pycloud.pycloud.vm.virtualmachinedescriptor import VirtualMachineDescriptor
from pycloud.pycloud.vm.virtualmachinedescriptor import VirtualMachineException
from pycloud.pycloud.vm.vmutils import get_hypervisor
from pycloud.pycloud.utils import portmanager
from pycloud.pycloud.cloudlet import get_cloudlet_instance

################################################################################################################
# Represents a runtime ServiceVM, independent on whether it has a cloned or original disk image.
################################################################################################################
class ServiceVM(Model):
    # Meta class is needed so that minimongo can map this class onto the database.
    class Meta:
        collection = "service_vms"
        external = ['_id', 'service_id', 'running', 'port', 'ip_address', 'vnc_address', 'ssh_port']
        mapping = {
            'vm_image': VMImage
        }

    # Constants.
    SSH_INTERNAL_PORT = 22

    ################################################################################################################
    # Constructor.
    ################################################################################################################
    def __init__(self, *args, **kwargs):
        self._id = None
        self.vm_image = None
        self.os = "lin"     # By default, used when creating a new SVM only.
        self.prefix = 'VM'
        self.port_mappings = {}
        self.service_port = None
        self.port = None    # Used to show the external port
        self.ssh_port = None
        self.vnc_address = None
        self.vnc_port = None
        self.service_id = None
        self.ip_address = None
        self.mac_address = None
        self.running = False
        super(ServiceVM, self).__init__(*args, **kwargs)

    ################################################################################################################
    # Sets up the internal network parameters, based on the config.
    ################################################################################################################
    def _setup_network(self):
        # Configure bridged mode if enabled
        c = get_cloudlet_instance()
        print 'Migration enabled: ', c.migration_enabled
        print 'Network Adapter: ', c.network_adapter
        if c.migration_enabled:
            self.network_mode = "bridged"
            self.adapter = c.network_adapter

            # In bridge mode we need a new MAC in case we are a clone.
            self.mac_address = generate_random_mac()
            print 'Generated new mac address: ' + self.mac_address
        else:
            self.network_mode = "user"
            self.adapter = c.network_adapter

    ################################################################################################################
    # Locate a servicevm by its ID
    ################################################################################################################
    # noinspection PyBroadException
    @staticmethod
    def by_id(svm_id=None):
        try:
            service_vm = ServiceVM.find_one({'_id': svm_id})
        except:
            return None
        return service_vm        

    ################################################################################################################
    # Generates a random ID, valid as a VM id.
    ################################################################################################################
    @staticmethod
    def by_service(service_id):
        return ServiceVM.find({'service_id': service_id})

    ################################################################################################################
    # Lookup a specific instance by its uuid
    ################################################################################################################
    @staticmethod
    def _get_virtual_machine(uuid):
        return get_hypervisor().lookupByUUIDString(uuid)

    ################################################################################################################
    # Cleanly and safely gets a ServiceVM and removes it from the database.
    ################################################################################################################
    @staticmethod
    def find_and_remove(svm_id):
        # Find the right service and remove it. find_and_modify will only return the document with matching id
        return ServiceVM.find_and_modify(query={'_id': svm_id}, remove=True)

    ################################################################################################################
    # Generates a random ID, valid as a VM id.
    ################################################################################################################
    def generate_random_id(self):
        self._id = str(uuid4())

    ################################################################################################################
    # Add a port mapping
    ################################################################################################################
    def add_port_mapping(self, host_port, guest_port):
        if not self.port_mappings:
            self.port_mappings = {}

        # If you are setting the services port we need to set the external port in a particular attribute.
        if guest_port == self.service_port:
            self.port = host_port
            
        # If you are setting the SSH port we need to set the external port in a particular attribute.
        if guest_port == self.SSH_INTERNAL_PORT:
            self.ssh_port = host_port               

        # Add the actual mapping.
        self.port_mappings[str(host_port)] = guest_port
        print('Setting up port forwarding from host port ' + str(host_port) + ' to guest port ' + str(guest_port))

    ################################################################################################################
    # Gets the port mappings in the form int -> int instead of str -> int
    ################################################################################################################
    def _get_libvirt_port_mappings(self):
        ret = {}
        if self.port_mappings:
            for key, value in self.port_mappings.iteritems():
                ret[int(key)] = value
        return ret
    
    ################################################################################################################
    # Updates an XML containing the description of the VM with the current info of this VM.
    ################################################################################################################    
    def _update_descriptor(self, saved_xml_descriptor):
        # Get the descriptor and inflate it to something we can work with.
        xml_descriptor = VirtualMachineDescriptor(saved_xml_descriptor)

        # Change the ID and Name (note: not currently that useful since they are changed in the saved state file).
        xml_descriptor.setUuid(self._id)
        xml_descriptor.setName(self.prefix + '-' + self._id)

        # Set the disk image in the description of the VM.
        xml_descriptor.setDiskImage(self.vm_image.disk_image, 'qcow2')

        # Enable remote VNC access.
        xml_descriptor.enableRemoteVNC()

        # Sets the Realtek network driver, needed for Windows-based VMs.
        if self.os != "lin":
            print "Setting Realtek network driver."
            xml_descriptor.setRealtekNetworkDriver()

        # Configure bridged mode if enabled
        if self.network_mode == "bridged":
            print 'Setting bridged mode'
            xml_descriptor.enableBridgedMode(self.adapter)

            # In bridge mode we need a new MAC in case we are a clone.
            print 'Setting mac address \'%s\'' % self.mac_address
            xml_descriptor.setMACAddress(self.mac_address)

            # Set external ports same as internal ones.
            self.port = self.service_port
            self.ssh_port = self.SSH_INTERNAL_PORT
        else:
            # No bridge mode, means we have to setup port forwarding.
            # Ensure we are not using bridged mode.
            xml_descriptor.enableNonBridgedMode(self.adapter)

            # Create a new port if we do not have an external port already.
            print 'Setting up port forwarding'
            if not self.port:
                self.add_port_mapping(portmanager.PortManager.generateRandomAvailablePort(), self.service_port)
            if not self.ssh_port:
                self.add_port_mapping(portmanager.PortManager.generateRandomAvailablePort(), self.SSH_INTERNAL_PORT)
            xml_descriptor.setPortRedirection(self._get_libvirt_port_mappings())

        # Get the resulting XML string and return it.
        updated_xml_descriptor = xml_descriptor.getAsString()
        return updated_xml_descriptor
    
    ################################################################################################################
    # Updates the name and id of an xml by simply replacing the text, without parsing, to ensure the result will
    # have exactly the same length as before.
    ################################################################################################################    
    def _update_raw_name_and_id(self, saved_xml_string):
        updated_xml = re.sub(r"<uuid>[\w\-]+</uuid>", "<uuid>%s</uuid>" % self._id, saved_xml_string)
        updated_xml = re.sub(r"<name>[\w\-]+</name>", "<name>%s</name>" % (self.prefix + '-' + self._id), updated_xml)
        return updated_xml

    ################################################################################################################
    # Updates the MAC of an xml by simply replacing the text, without parsing, to ensure the result will
    # have the exact same length as before.
    ################################################################################################################
    def _update_raw_mac(self, saved_xml_string):
        updated_xml = re.sub(r"<mac address='[\w\d:]+'/>", "<mac address='%s'/>" % self.mac_address, saved_xml_string)
        return updated_xml

    ################################################################################################################
    # Waits for the service to boot up.
    ################################################################################################################
    def _wait_for_service(self, retries=5):
        if retries == 0:
            print 'Service is not available, stopping retries.'
            return False

        print 'Checking if service is available inside VM.'
        result = is_port_open(self.ip_address, int(self.port))
        if not result:
            print 'Service is not yet available, waiting...'
            time.sleep(2)
            return self._wait_for_service(retries=(retries-1))
        else:
            print 'Successful connection, service is available.'
            return True

    ################################################################################################################
    # Will locate the IP address from our MAC.
    ################################################################################################################
    def _get_ip_from_mac(self):
        # mac_address will have a value if bridged mode is enabled
        if self.mac_address is None:
            raise Exception("IP address could not be obtained since the VM has no MAC address set up.")

        print "Retrieving IP for MAC: %s" % self.mac_address
        ip = find_ip_for_mac(self.mac_address, self.adapter)
        if not ip:
            print "Failed to locate the IP of the VM."
            raise Exception('Failed to locate the IP of the VM.')

        return ip

    ################################################################################################################
    # Boots a VM using a defined disk image and a state XML.
    ################################################################################################################
    def _cold_boot(self, xml_descriptor):
        # Create a VM ("domain") through the hypervisor.
        print "Booting up a VM..."
        try:
            get_hypervisor().createXML(xml_descriptor, 0)
            print "VM object successfully created, VM started."
            self.running = True
        except:
            # Ensure we destroy the VM if there was some problem after creating it.
            self.destroy()
            raise

    ################################################################################################################
    # Perform several network checks: get the IP of the VM, ensure that the service is available, and get the VNC
    # address and port.
    ################################################################################################################
    def _network_checks(self, check_service=True):
        try:
            # Get the IP of the VM.
            if self.network_mode == 'bridged':
                # We will attempt to indirectly get the IP from the virtual MAC of the VM.
                self.ip_address = self._get_ip_from_mac()
            else:
                # If we are not on bridged mode, the VM's IP address will be the same as the cloudlet's address.
                self.ip_address = get_adapter_ip_address(self.adapter)
        except Exception as e:
            import traceback
            traceback.print_exc()
            # TODO: throw exception.
            print "Error getting IP of new SVM: " + str(e)
            check_service = False
        print "SSH available on {}:{}".format(str(self.ip_address), str(self.ssh_port))

        if check_service:
            # Wait until the service is running inside the VM.
            service_available = self._wait_for_service()
            if not service_available:
                # TODO: throw exception.
                print 'Service was not found running inside the SVM. Check if it is configured to start at boot time.'

        # Get VNC connection info.
        self.vnc_address = self.__get_vnc_address()
        self.vnc_port = self.__get_vnc_port()
        print "VNC available on {}".format(str(self.vnc_address))

    ################################################################################################################
    # Create a new service VM from a given template, and start it.
    ################################################################################################################
    def create(self, vm_xml_template_file):
        # Check that the XML description file exists.
        if not os.path.exists(vm_xml_template_file):
            raise VirtualMachineException("VM description file %s for VM creation does not exist." % vm_xml_template_file)

        # Setup network params.
        self._setup_network()

        # Load the XML template and update it with this VM's information.
        template_xml_descriptor = open(vm_xml_template_file, "r").read()
        updated_xml_descriptor = self._update_descriptor(template_xml_descriptor)

        # Create a VM ("domain") through the hypervisor.
        self._cold_boot(updated_xml_descriptor)

        # Ensure network is working and load network data.
        self._network_checks(check_service=False)

        return self

    ################################################################################################################
    # Start this service VM. 
    ################################################################################################################
    def start(self):
        # Check if we are already running.
        if self.running:
            return self

        # Setup network params.
        self._setup_network()

        # Make sure libvirt can write to our files (since the disk image will be modified by the VM).
        self.vm_image.unprotect()

        # Get the saved state and make sure it is populated
        saved_state = VMSavedState(self.vm_image.state_image)

        # Update the state image with the updated descriptor.
        # NOTE: this is only needed since libvirt wont allow us to change the ID of a VM being restored through its API. 
        # Instead, we trick it by manually changing the ID of the saved state file, so the API won't know we changed it. 
        raw_saved_xml_descriptor = saved_state.getRawStoredVmDescription(get_hypervisor())
        updated_xml_descriptor_id_only = self._update_raw_name_and_id(raw_saved_xml_descriptor)
        saved_state.updateStoredVmDescription(updated_xml_descriptor_id_only)

        # Get the descriptor and update it to include the current disk image path, port mappings, etc.
        saved_xml_descriptor = saved_state.getStoredVmDescription(get_hypervisor())
        updated_xml_descriptor = self._update_descriptor(saved_xml_descriptor)

        # Restore a VM to the state indicated in the associated memory image file, in running mode.
        # The XML descriptor is given since some things need to be changed for the instance, mainly the disk image file and the mapped ports.
        try:
            print "Resuming from VM image..."
            get_hypervisor().restoreFlags(saved_state.savedStateFilename, updated_xml_descriptor, libvirt.VIR_DOMAIN_SAVE_RUNNING)
            print "Resumed from VM image."
            self.running = True
        except libvirt.libvirtError as e:
            # If we could not resume the VM, discard the memory state and try to boot the VM from scratch.
            print "Error resuming VM: %s for VM; error is: %s" % (str(self._id), str(e))
            print "Discarding saved state and attempting to cold boot VM."
            
            # Simply try creating a new VM with the same disk and the updated XML descriptor from the saved state file.
            self._cold_boot(updated_xml_descriptor)

        # Ensure network is working and load network data.
        self._network_checks()

        return self

    ################################################################################################################
    # Gets the host port the VNC server is listening on for this vm, which was automatically allocated by libvirt/qemu.
    ################################################################################################################
    def __get_vnc_port(self):
        vm_xml_string = ServiceVM._get_virtual_machine(self._id).XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE)
        xml_descriptor = VirtualMachineDescriptor(vm_xml_string)
        vnc_port = xml_descriptor.getVNCPort()
        return vnc_port

    ################################################################################################################
    # Gets the host IP and por port the VNC server is listening on for this vm, which was automatically allocated by libvirt/qemu.
    ################################################################################################################
    def __get_vnc_address(self):
        return get_adapter_ip_address(self.adapter) + ":" + self.__get_vnc_port()

    ################################################################################################################
    # Stop this service VM
    ################################################################################################################
    def stop(self, foce_save_state=False):
        # Check if this instance is actually running
        if not self.running:
            return

        vm = None
        try:
            # Get the VM
            vm = ServiceVM._get_virtual_machine(self._id)

            # Save the state, if our image is not cloned.
            if not self.vm_image.cloned or foce_save_state:
                self._save_state()
                self.running = False
        except Exception, e:
            print "Warning getting VM: " + str(e)

        # Destroy the VM if it exists, anr mark it as not running.
        if vm and self.running:
            print "Stopping Service VM with instance id %s" % self._id
            vm.destroy()
        else:
            print 'VM with id %s not found while stopping it.' % self._id
        self.running = False

    ################################################################################################################
    # Pauses a VM.
    ################################################################################################################
    def pause(self):
        vm = ServiceVM._get_virtual_machine(self._id)
        result = vm.suspend()
        self.running = False
        return result

    ################################################################################################################
    # Unpauses a VM.
    ################################################################################################################
    def unpause(self):
        vm = ServiceVM._get_virtual_machine(self._id)
        result = vm.resume()
        if result == 0:
            self.running = True
        return result

    ################################################################################################################
    # Migrates a vm.
    ################################################################################################################
    def migrate(self, remote_host, p2p=False):
            vm = ServiceVM._get_virtual_machine(self._id)

            # Prepare basic flags. Bandwidth 0 lets libvirt choose the best value
            # (and some hypervisors do not support it anyway).
            # TODO: figure out why shared disk is ignored.
            flags = 0 # libvirt.VIR_MIGRATE_NON_SHARED_DISK | libvirt.VIR_MIGRATE_PAUSED
            new_id = None
            bandwidth = 0

            # Set flags that depend on migration type.
            print 'Starting memory and state migration...'
            start_time = time.time()
            if p2p:
                flags = flags | libvirt.VIR_MIGRATE_PEER2PEER
                #uri = 'tcp://%s' % remote_host
                uri = None
            else:
                uri = None

            # Migrate the state and memory.
            remote_uri = 'qemu://%s/system' % remote_host
            remote_hypervisor = libvirt.open(remote_uri)
            vm.migrate(remote_hypervisor, flags, new_id, uri, bandwidth)

            elapsed_time = time.time() - start_time
            print 'Migration finished successfully. It took ' + str(elapsed_time) + ' seconds.'

    ################################################################################################################
    # Pauses a VM and stores its memory state to a disk file.
    ################################################################################################################          
    def _save_state(self):
        # Get the VM.
        vm = ServiceVM._get_virtual_machine(self._id)     
        
        # We indicate that we want want to use as much bandwidth as possible to store the VM's memory when suspending.
        unlimitedBandwidth = 1000000    # In Gpbs
        vm.migrateSetMaxSpeed(unlimitedBandwidth, 0)

        # Store the VM's memory state to a file.
        print "Storing VM memory state to file %s" % self.vm_image.state_image
        try:
            result = vm.save(self.vm_image.state_image)
            if result != 0:
                raise VirtualMachineException("Cannot save memory state to file %s", str(self._id))
            else:
                print "Memory state successfully saved."
        except libvirt.libvirtError, e:
            raise VirtualMachineException(str(e))

    ################################################################################################################
    # Will delete this VM (and stop it if it is currently running)
    ################################################################################################################
    def destroy(self):
        if self.running:
            try:
                self.stop()
            except Exception, e:
                print "Warning: error while cleaning up VM: " + str(e)

        # Remove VM files, and remove it from the database of running VMs.
        self.vm_image.cleanup()
        ServiceVM.find_and_remove(self._id)
