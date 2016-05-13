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

import time
import os
import json

# Used to generate unique IDs for the VMs.
from uuid import uuid4

from pycloud.pycloud.utils.netutils import generate_random_mac, find_ip_for_mac, is_port_open, get_adapter_ip_address

from pycloud.pycloud.mongo import Model
from pycloud.pycloud.model.vmimage import VMImage
from pycloud.pycloud.vm.vmsavedstate import VMSavedState
from pycloud.pycloud.vm.virtualmachinedescriptor import VirtualMachineDescriptor
from pycloud.pycloud.vm.vmutils import VirtualMachineException
from pycloud.pycloud.utils import portmanager
from pycloud.pycloud.cloudlet import get_cloudlet_instance
from pycloud.pycloud.vm.vmutils import VirtualMachine

from pycloud.pycloud.network import cloudlet_dns


################################################################################################################
#
################################################################################################################
class SVMNotFoundException(Exception):
    def __init__(self, message):
        super(SVMNotFoundException, self).__init__(message)
        self.message = message


################################################################################################################
# Represents a runtime ServiceVM, independent on whether it has a cloned or original disk image.
################################################################################################################
class ServiceVM(Model):
    # Meta class is needed so that minimongo can map this class onto the database.
    class Meta:
        collection = "service_vms"
        external = ['_id', 'service_id', 'running', 'port', 'ip_address', 'vnc_address', 'ssh_port', 'fqdn']
        mapping = {
            'vm_image': VMImage
        }

    # Constants.
    SSH_INTERNAL_PORT = 22
    VM_NAME_PREFIX = 'VM'

    ################################################################################################################
    # Constructor.
    ################################################################################################################
    def __init__(self, *args, **kwargs):
        self._id = None
        self.vm = VirtualMachine()
        self.vm_image = None
        self.os = 'lin'     # By default, used when creating a new SVM only.
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
        self.ready = False
        self.fqdn = None
        self.network_mode = None
        self.adapter = None
        self.num_current_users = 0
        super(ServiceVM, self).__init__(*args, **kwargs)

    ################################################################################################################
    # Locate a ServiceVM by its ID
    ################################################################################################################
    # noinspection PyBroadException
    @staticmethod
    def by_id(svm_id=None, only_find_ready_ones=True):
        try:
            search_dict = {'_id': svm_id}
            if only_find_ready_ones:
                search_dict['ready'] = True
            service_vm = ServiceVM.find_one(search_dict)
        except:
            return None

        if service_vm:
            service_vm.vm = VirtualMachine()
            try:
                service_vm.vm.connect_to_virtual_machine(service_vm._id)
            except VirtualMachineException as e:
                print 'Error connecting to VM with id {}: {}'.format(svm_id, e.message)
                service_vm.vm = None

        return service_vm

    ################################################################################################################
    #
    ################################################################################################################
    @staticmethod
    def by_service(service_id):
        service_vms_array = []
        service_vms = ServiceVM.find({'service_id': service_id})
        for service_vm in service_vms:
            service_vm.vm = VirtualMachine()
            service_vm.vm.connect_to_virtual_machine(service_vm._id)
            service_vms_array.append(service_vm)
        return service_vms_array

    ################################################################################################################
    # Cleanly and safely gets a ServiceVM and removes it from the database.
    ################################################################################################################
    @staticmethod
    def find_and_remove(svm_id):
        # Find the right service and remove it. find_and_modify will only return the document with matching id
        return ServiceVM.find_and_modify(query={'_id': svm_id}, remove=True)

    ################################################################################################################
    # Overridden method to avoid trying to store the VM object into the db.
    ################################################################################################################
    def save(self, *args, **kwargs):
        vm = self.vm
        self.vm = None
        super(ServiceVM, self).save(*args, **kwargs)
        self.vm = vm

    ################################################################################################################
    # Serializes the object safely into a json string.
    ################################################################################################################
    def to_json_string(self):
        vm = self.vm
        self.vm = None
        json_string = json.dumps(self)
        self.vm = vm
        return json_string

    ################################################################################################################
    #
    ################################################################################################################
    def get_name(self):
        return self.VM_NAME_PREFIX + '-' + self._id

    ################################################################################################################
    # Generates a random ID, valid as a VM id.
    ################################################################################################################
    def generate_random_id(self):
        self._id = str(uuid4())

    ################################################################################################################
    # Create a new service VM from a given template, and start it.
    ################################################################################################################
    def create(self, vm_xml_template_file):
        # Check that the XML description file exists.
        if not os.path.exists(vm_xml_template_file):
            raise VirtualMachineException("VM description file %s for VM creation does not exist." % vm_xml_template_file)

        # Setup network params.
        self.setup_network()

        # Load the XML template and update it with this VM's information.
        template_xml_descriptor = open(vm_xml_template_file, "r").read()
        updated_xml_descriptor = self._update_descriptor(template_xml_descriptor)

        # Create a VM ("domain") through the hypervisor.
        self._cold_boot(updated_xml_descriptor)

        # Ensure network is working and load network data.
        self.load_network_data()
        self.register_with_dns()

        return self

    ################################################################################################################
    # Start this service VM. 
    ################################################################################################################
    def start(self):
        # Check if we are already running.
        if self.running:
            return self

        # Setup network params.
        self.setup_network()

        # Make sure the hypervisor can write to our files (since the disk image will be modified by the VM).
        self.vm_image.unprotect()

        # Get the saved state and make sure it is populated
        saved_state = VMSavedState(self.vm_image.state_image)

        # Update the state image with the updated descriptor.
        # NOTE: this is only needed since libvirt wont allow us to change the ID of a VM being restored through its API. 
        # Instead, we trick it by manually changing the ID of the saved state file, so the API won't know we changed it. 
        raw_saved_xml_descriptor = saved_state.getRawStoredVmDescription()
        updated_xml_descriptor_id_only = VirtualMachineDescriptor.update_raw_name_and_id(raw_saved_xml_descriptor,
                                                                                         self._id, self.get_name())
        saved_state.updateStoredVmDescription(updated_xml_descriptor_id_only)

        # Get the descriptor and update it to include the current disk image path, port mappings, etc.
        saved_xml_descriptor = saved_state.getStoredVmDescription()
        updated_xml_descriptor = self._update_descriptor(saved_xml_descriptor)

        # Restore a VM to the state indicated in the associated memory image file, in running mode.
        # The XML descriptor is given since some things need to be changed for the instance, mainly the disk image file and the mapped ports.
        try:
            print "Resuming from VM image..."
            VirtualMachine.restore_saved_vm(saved_state.savedStateFilename, updated_xml_descriptor)
            self.vm.connect_to_virtual_machine(self._id)
            print "Resumed from VM image."
            self.running = True
            self.ready = True
        except VirtualMachineException as e:
            # If we could not resume the VM, discard the memory state and try to boot the VM from scratch.
            print "Error resuming VM: %s for VM; error is: %s" % (str(self._id), str(e))
            print "Discarding saved state and attempting to cold boot VM."
            
            # Simply try creating a new VM with the same disk and the updated XML descriptor from the saved state file.
            self._cold_boot(updated_xml_descriptor)

        # Ensure network is working and load network data.
        self.load_network_data()
        self.register_with_dns()

        # Check if the service is available, wait for it for a bit.
        self._check_service()

        return self

    ################################################################################################################
    # Updates an XML containing the description of the VM with the current info of this VM.
    ################################################################################################################
    def _update_descriptor(self, saved_xml_descriptor):
        # Get the descriptor and inflate it to something we can work with.
        xml_descriptor = VirtualMachineDescriptor(saved_xml_descriptor)

        # Change the ID and Name (note: not currently that useful since they are changed in the saved state file).
        xml_descriptor.setUuid(self._id)
        xml_descriptor.setName(self.get_name())

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
                self._add_port_mapping(portmanager.PortManager.generate_random_available_port(), self.service_port)
            if not self.ssh_port:
                self._add_port_mapping(portmanager.PortManager.generate_random_available_port(), self.SSH_INTERNAL_PORT)
            xml_descriptor.setPortRedirection(self.port_mappings)

        # Remove seclabel item.
        xml_descriptor.removeSecLabel()

        # Get the resulting XML string and return it.
        updated_xml_descriptor = xml_descriptor.getAsString()
        return updated_xml_descriptor

    ################################################################################################################
    # Add a port mapping
    ################################################################################################################
    def _add_port_mapping(self, host_port, guest_port):
        if not self.port_mappings:
            self.port_mappings = {}

        # If you are setting the services port we need to set the external port in a particular attribute.
        if guest_port == self.service_port:
            self.port = host_port

        # If you are setting the SSH port we need to set the external port in a particular attribute.
        if guest_port == self.SSH_INTERNAL_PORT:
            self.ssh_port = host_port

        # Add the actual mapping. Keys need to be stored as string so that MongoDB will accept and store them.
        self.port_mappings[str(host_port)] = int(guest_port)
        print('Setting up port forwarding from host port ' + str(host_port) + ' to guest port ' + str(guest_port))

    ################################################################################################################
    # Boots a VM using a defined disk image and a state XML.
    ################################################################################################################
    def _cold_boot(self, xml_descriptor):
        # Create a VM ("domain") through the hypervisor.
        print "Booting up a VM..."
        try:
            self.vm.create_and_start_vm(xml_descriptor)
            print "VM object successfully created, VM started."
            self.running = True
            self.ready = True
        except:
            # Ensure we destroy the VM if there was some problem after creating it.
            self.stop()
            raise

    ################################################################################################################
    # Sets up the internal network parameters, based on the config.
    ################################################################################################################
    def setup_network(self, update_mac_if_needed=True):
        # Configure bridged mode if enabled
        c = get_cloudlet_instance()
        print 'Bridge enabled: ', c.network_bridge_enabled
        print 'Network Adapter: ', c.network_adapter
        if c.network_bridge_enabled:
            self.network_mode = "bridged"
            self.adapter = c.network_adapter

            if update_mac_if_needed:
                # In bridge mode we need a new MAC in case we are a clone.
                self.mac_address = generate_random_mac()
                print 'Generated new mac address: ' + self.mac_address
        else:
            self.network_mode = "user"
            self.adapter = c.network_adapter

        # Generate FQDN.
        self._generate_fqdn()

    ################################################################################################################
    # Set up network stuff.
    ################################################################################################################
    def load_network_data(self):
        self._load_ip_address()
        self._load_vnc_address_from_running_instance()

    ################################################################################################################
    # Loads network data: get the IP of the VM.
    ################################################################################################################
    def _load_ip_address(self):
        try:
            # Get the IP of the VM.
            if self.network_mode == 'bridged':
                if self.ip_address is None:
                    # We will attempt to indirectly get the IP from the virtual MAC of the VM.
                    self.ip_address = self._get_ip_from_mac()
            else:
                # If we are not on bridged mode, the VM's IP address will be the same as the cloudlet's address.
                self.ip_address = get_adapter_ip_address(self.adapter)
        except Exception as e:
            message = "Error getting IP of new SVM: " + str(e)
            raise Exception(message)

        print "SSH available on {}:{}".format(str(self.ip_address), str(self.ssh_port))

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

    ###############################################################################################################
    # Get the VNC address and port, loading it from the running VM.
    ###############################################################################################################
    def _load_vnc_address_from_running_instance(self):
        try:
            self.vnc_port = self._get_vnc_port()
            self.vnc_address = get_adapter_ip_address(self.adapter) + ":" + self.vnc_port
            print "VNC available on {}".format(str(self.vnc_address))
        except Exception, e:
            print 'Could not load VNC address: ' + str(e)

    ################################################################################################################
    # Gets the host port the VNC server is listening on for this vm, which was automatically allocated.
    ################################################################################################################
    def _get_vnc_port(self):
        vm_xml_string = self.vm.get_running_vm_xml_string()
        xml_descriptor = VirtualMachineDescriptor(vm_xml_string)
        vnc_port = xml_descriptor.getVNCPort()
        return vnc_port

    ################################################################################################################
    # Checks if the service is running inside the VM.
    ################################################################################################################
    def _check_service(self):
        # Wait until the service is running inside the VM.
        service_available = self._wait_for_service()
        if not service_available:
            # TODO: throw exception.
            print 'Service was not found running inside the SVM. Check if it is configured to start at boot time.'

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
            return self._wait_for_service(retries=(retries - 1))
        else:
            print 'Successful connection, service is available.'
            return True

    ################################################################################################################
    # Generates a FQDN for the SVM.
    ################################################################################################################
    def _generate_fqdn(self):
        hostname = self.service_id + '.' + self._id
        self.fqdn = cloudlet_dns.CloudletDNS.generate_fqdn(hostname)

    ################################################################################################################
    # Register with DNS server.
    ################################################################################################################
    def register_with_dns(self):
        # Register with DNS. If we are in bridged mode, we need to set up a specific record to the new IP address.
        dns_server = cloudlet_dns.CloudletDNS(get_cloudlet_instance().data_folder)
        if self.network_mode == 'bridged':
            dns_server.register_svm(self.fqdn, self.ip_address)
        else:
            dns_server.register_svm(self.fqdn)

    ################################################################################################################
    # Stop this service VM, removing its files, database records, and other related records.
    ################################################################################################################
    def stop(self, foce_save_state=False, cleanup_files=True):
        # Check if this instance is actually running
        if self.running:
            try:
                # Save the state, if our image is not cloned.
                if not self.vm_image.cloned or foce_save_state:
                    self._save_state()
                    self.running = False

                # Destroy the VM if it exists, and mark it as not running.
                if self.vm and self.running:
                    print "Stopping Service VM with instance id %s" % self._id
                    self.vm.destroy()
                else:
                    print 'VM with id %s not found while stopping it.' % self._id
                self.running = False
                self.ready = False
            except Exception, e:
                print "Warning: error while cleaning up VM: " + str(e)

        # Unregister from DNS.
        try:
            dns_server = cloudlet_dns.CloudletDNS(get_cloudlet_instance().data_folder)
            dns_server.unregister_svm(self.fqdn)
        except Exception, e:
            print "Warning: error while removing DNS record: " + str(e)

        # Remove it from the database of running VMs.
        ServiceVM.find_and_remove(self._id)

        if cleanup_files:
            # Remove VM files
            self.vm_image.cleanup()

    ################################################################################################################
    # Pauses a VM and stores its memory state to a disk file.
    ################################################################################################################
    def _save_state(self):
        print "Storing VM memory state to file %s" % self.vm_image.state_image
        self.vm.save_state(self.vm_image.state_image)
        print "Memory state successfully saved."

    ################################################################################################################
    # Pauses a VM.
    ################################################################################################################
    def pause(self):
        result = self.vm.pause()
        self.running = False
        return result

    ################################################################################################################
    # Unpauses a VM.
    ################################################################################################################
    def unpause(self):
        result = self.vm.unpause()
        was_resume_successful = result == 0
        if was_resume_successful:
            self.running = True
            self.ready = True
        return was_resume_successful

    ################################################################################################################
    # Migrates a vm.
    ################################################################################################################
    def migrate(self, remote_host):
        # Set flags that depend on migration type.
        print 'Starting memory and state migration...'
        start_time = time.time()

        # Migrate the state and memory.
        self.vm.perform_memory_migration(remote_host)

        # Unregister from DNS server.
        dns_server = cloudlet_dns.CloudletDNS(get_cloudlet_instance().data_folder)
        dns_server.unregister_svm(self.fqdn)

        elapsed_time = time.time() - start_time
        print 'Migration finished successfully. It took ' + str(elapsed_time) + ' seconds.'

    ################################################################################################################
    # Stops and clears all registered SVMs.
    ################################################################################################################
    @staticmethod
    def clear_all_svms():
        print 'Shutting down all running virtual machines'
        svm_list = ServiceVM.find()
        for svm in svm_list:
            svm.vm = VirtualMachine()
            svm.vm.connect_to_virtual_machine(svm._id)
            svm.stop()

        print 'All machines shutdown.'
