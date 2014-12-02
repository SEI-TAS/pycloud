__author__ = 'jdroot'

# Import libvirt to access the virtualization API.
import libvirt

import re
import random
import time
import os

# Used to generate unique IDs for the VMs.
from uuid import uuid4

from pycloud.pycloud.mongo import Model
from pycloud.pycloud.model.vmimage import VMImage
from pycloud.pycloud.vm.vmsavedstate import VMSavedState
from pycloud.pycloud.vm.virtualmachinedescriptor import VirtualMachineDescriptor
from pycloud.pycloud.vm.virtualmachinedescriptor import VirtualMachineException
from pycloud.pycloud.vm.vncclient import VNCClient
from pycloud.pycloud.vm.vmutils import HYPERVISOR_URI
from pycloud.pycloud.utils import portmanager
from pycloud.pycloud.cloudlet import get_cloudlet_instance

from subprocess import Popen, PIPE
from xml.etree import ElementTree

################################################################################################################
# Represents a runtime ServiceVM, independent on whether it has a cloned or original disk image.
################################################################################################################
class ServiceVM(Model):
    # Meta class is needed so that minimongo can map this class onto the database.
    class Meta:
        collection = "service_vms"
        external = ['_id', 'service_id', 'running', 'port', 'ip_address']
        mapping = {
            'vm_image': VMImage
        }

    # URI used to connect to the local hypervisor.
    _HYPERVISOR_URI = HYPERVISOR_URI
    _hypervisor = None
    
    # Constants.
    SSH_INTERNAL_PORT = 22

    ################################################################################################################
    # Constructor.
    ################################################################################################################
    def __init__(self, *args, **kwargs):
        self._id = None
        self.vm_image = None
        self.prefix = 'VM'
        self.port_mappings = {}
        self.service_port = None
        self.port = None  # Used to show the external port
        self.ssh_port = None
        self.vnc_port = None
        self.service_id = None
        self.ip_address = None
        self.mac_address = None
        self.running = False
        super(ServiceVM, self).__init__(*args, **kwargs)
        
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
    # Returns the hypervisor connection and will auto connect if the connection is null
    ################################################################################################################
    @staticmethod
    def get_hypervisor():
        if not ServiceVM._hypervisor:
            ServiceVM._hypervisor = libvirt.open(ServiceVM._HYPERVISOR_URI)
        return ServiceVM._hypervisor

    ################################################################################################################
    # Lookup a specific instance by its uuid
    ################################################################################################################
    @staticmethod
    def _get_virtual_machine(uuid):
        return ServiceVM.get_hypervisor().lookupByUUIDString(uuid)

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
    # Generates a random MAC address.
    ################################################################################################################
    def generate_random_mac(self):
        mac = [
            0x00, 0x16, 0x3e,
            random.randint(0x00, 0x7f),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff)
        ]
        return ':'.join(map(lambda x: "%02x" % x, mac))

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
        """
        :rtype : (string, string)
        """
        xml_descriptor = VirtualMachineDescriptor(saved_xml_descriptor)

        # Change the ID and Name (note: not currently that useful since they are changed in the saved state file).
        xml_descriptor.setUuid(self._id)
        xml_descriptor.setName(self.prefix + '-' + self._id)

        # Set the disk image in the description of the VM.
        xml_descriptor.setDiskImage(self.vm_image.disk_image, 'qcow2')

        # Enable remote VNC access.
        xml_descriptor.enableRemoteVNC()

        # Configure bridged mode if enabled
        c = get_cloudlet_instance()
        print 'Migration enabled: ', c.migration_enabled
        print 'Bridge Adapter: ', c.bridge_adapter
        if c.migration_enabled and c.bridge_adapter:
            print 'Enabling bridged mode'
            xml_descriptor.enableBridgedMode('br0')

            # In bridge mode we need a new MAC in case we are a clone.
            print 'Generating new mac address'
            self.mac_address = self.generate_random_mac()
            xml_descriptor.setMACAddress(self.mac_address)
            print 'Set mac address \'%s\'' % self.mac_address

            self.port = self.service_port
            self.ssh_port = self.SSH_INTERNAL_PORT
        else:
            # No bridge mode, means we have to setup port forwarding.
            # Create a new port if we do not have an external port already.
            if not self.port:
                self.add_port_mapping(portmanager.PortManager.generateRandomAvailablePort(), self.service_port)
            if not self.ssh_port:
                self.add_port_mapping(portmanager.PortManager.generateRandomAvailablePort(), self.SSH_INTERNAL_PORT)
            xml_descriptor.setPortRedirection(self._get_libvirt_port_mappings())

        # Get the resulting XML string and return it.
        updated_xml_descriptor = xml_descriptor.getAsString()
        # print '===================================='
        # print updated_xml_descriptor
        # print '===================================='
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
    # Will locate the IP address for a given mac address
    ################################################################################################################
    @staticmethod
    def _find_ip_for_mac(mac, retry=3):
        if retry == 0:
            print ''
            return None
        c = get_cloudlet_instance()

        p = Popen(['sudo', c.nmap, '-sP', c.nmap_ip, '-oX', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out,err = p.communicate()
        rc = p.returncode
        if rc != 0:
            print "Error executing nmap:\n%s" % err
            return None
        xml = ElementTree.fromstring(out)
        ip = None
        try:
            ip = xml.find('./host/address[@addr="%s"]/../address[@addrtype="ipv4"]' % mac.upper()).get('addr')
            print 'Found IP: ', ip
        except:
            print 'Failed to find IP, retrying...'
            ip = ServiceVM._find_ip_for_mac(mac, retry=(retry - 1))

        return ip

    ################################################################################################################
    # Will locate the IP address if we have a MAC address
    ################################################################################################################
    def _set_ip_if_mac(self, mac):
        # mac_address will have a value if bridged mode is enabled
        if mac is not None:
            print "Retrieving IP for MAC: %s" % mac
            ip = ServiceVM._find_ip_for_mac(mac)
            if not ip:
                print "Failed to locate the IP for the server!!!!"
                # TODO: Possibly throw an exception and shutdown the VM
            else:
                self.ip_address = ip
                self.mac_address = mac

    ################################################################################################################
    # Create a new service VM from a given template, and start it.
    ################################################################################################################
    def create(self, vmXmlTemplateFile):
        # Check that the XML description file exists.
        if(not os.path.exists(vmXmlTemplateFile)):
            raise VirtualMachineException("VM description file %s for VM creation does not exist." % vmXmlTemplateFile)
         
        # Load the XML template and update it with this VM's information.
        template_xml_descriptor = open(vmXmlTemplateFile, "r").read()
        updated_xml_descriptor = self._update_descriptor(template_xml_descriptor)

        # Create a VM ("domain") through the hypervisor.
        print "Starting a new VM..."  
        try:
            ServiceVM.get_hypervisor().createXML(updated_xml_descriptor, 0)
            print "VM successfully created and started."

            self._set_ip_if_mac(self.mac_address)

            self.vnc_port = self.__get_vnc_port()
            print "VNC available on localhost:{}".format(str(self.vnc_port))
        except:
            # Ensure we destroy the VM if there was some problem after creating it.
            self.destroy()
            raise
        
        # When creating we start running.
        self.running = True

    ################################################################################################################
    # Start this service VM. 
    ################################################################################################################
    def start(self):
        # Check if we are already running.
        if self.running:
            return self
        
        # Make sure libvirt can write to our files (since the disk image will be modified by the VM).
        self.vm_image.unprotect()

        # Get the saved state and make sure it is populated
        saved_state = VMSavedState(self.vm_image.state_image)

        # Update the state image with the updated descriptor.
        # NOTE: this is only needed since libvirt wont allow us to change the ID of a VM being restored through its API. 
        # Instead, we trick it by manually changing the ID of the saved state file, so the API won't know we changed it. 
        raw_saved_xml_descriptor = saved_state.getRawStoredVmDescription(ServiceVM.get_hypervisor())
        updated_xml_descriptor_id_only = self._update_raw_name_and_id(raw_saved_xml_descriptor)
        saved_state.updateStoredVmDescription(updated_xml_descriptor_id_only)

        # Get the descriptor and update it to include the current disk image path, port mappings, etc.
        saved_xml_descriptor = saved_state.getStoredVmDescription(ServiceVM.get_hypervisor())
        updated_xml_descriptor = self._update_descriptor(saved_xml_descriptor)

        # TEST: Update the MAC address directly in the saved state file.
        #if self.mac_address:
            #print 'Updating saved state file MAC address to ' + self.mac_address
            #raw_saved_xml_descriptor = saved_state.getRawStoredVmDescription(ServiceVM.get_hypervisor())
            #updated_xml_descriptor_mac_only = self._update_raw_mac(raw_saved_xml_descriptor)
            #saved_state.updateStoredVmDescription(updated_xml_descriptor_mac_only)

        # Restore a VM to the state indicated in the associated memory image file, in running mode.
        # The XML descriptor is given since some things need to be changed for the instance, mainly the disk image file and the mapped ports.
        try:
            print "Resuming from VM image..."
            ServiceVM.get_hypervisor().restoreFlags(saved_state.savedStateFilename, updated_xml_descriptor, libvirt.VIR_DOMAIN_SAVE_RUNNING)
            print "Resumed from VM image."

            self._set_ip_if_mac(self.mac_address)

        except libvirt.libvirtError as e:
            # If we could not resume the VM, discard the memory state and try to boot the VM from scratch.
            print "Error resuming VM: %s for VM; error is: %s" % (str(self._id), str(e))
            print "Discarding saved state and attempting to cold boot VM."
            
            # Simply try creating a new VM with the same disk image and XML descriptor.
            try:
                ServiceVM.get_hypervisor().createXML(updated_xml_descriptor, 0)
                print "VM reboot was successful."

                self._set_ip_if_mac(self.mac_address)
            except:
                # Ensure we destroy the VM if there was some problem after creating it.
                self.destroy()
                raise

        self.vnc_port = self.__get_vnc_port()
        print "VNC available on localhost:{}".format(str(self.vnc_port))
        self.running = True

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
    # Starts a VNC connection with a GUI, and, if given in the argument, waits until it is closed.
    ################################################################################################################            
    def open_vnc(self, wait=True):
        # Get the VNC port, which was automatically allocated by libvirt/qemu.
        vnc_port = self.__get_vnc_port()
        
        # Connect through the VNC client and wait if required.
        print 'Starting VNC GUI to VM (on port {}).'.format(str(vnc_port))
        if wait:
            print 'Waiting for user to close VNC GUI.'
        vnc_client = VNCClient()
        success = vnc_client.connectAndWait(vnc_port, wait)

        if success:
            if wait:
                print 'VNC GUI no longer running, stopped waiting.'
            else:
                print 'VNC GUI has been opened.'
        else:
            # If there was a problem, destroy the VM.
            print 'VNC GUI could not be opened.'
            self.destroy()

    ################################################################################################################
    # Stop this service VM
    ################################################################################################################
    def stop(self, foce_save_state=False):
        # Check if this instance is actually running
        if not self.running:
            return

        print "Stopping Service VM with instance id %s" % self._id

        # TODO: self.closeSSHConnection()

        vm = ServiceVM._get_virtual_machine(self._id)
        if not vm:  # No VM for this ID found
            return
        
        # Save the state, if our image is not cloned.
        if not self.vm_image.cloned or foce_save_state:
            self._save_state()
            
        # Destroy it.
        try:
            vm = ServiceVM._get_virtual_machine(self._id)
            if vm:            
                vm.destroy()
        except:
            print 'VM not found while destroying it.'
        finally:
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
        
        # We first pause the VM.
        result = vm.suspend()
        if(result == -1):
            raise VirtualMachineException("Cannot pause VM: %s", str(self._id))
        
        # Store the VM's memory state to a disk image file.
        print "Storing VM memory state to file %s" % self.vm_image.state_image
        result = 0
        try:
            result = vm.save(self.vm_image.state_image)
        except libvirt.libvirtError, e:
            raise VirtualMachineException(str(e))
        if result != 0:
            raise VirtualMachineException("Cannot save memory state to file %s", str(self._id))

    ################################################################################################################
    # Will delete this VM (and stop it if it is currently running)
    ################################################################################################################
    def destroy(self):
        if self.running:
            try:
                self.stop()
            except Exception, e:
                print "Warning: error while cleaning up VM: " + str(e)
        self.vm_image.cleanup()
        ServiceVM.find_and_remove(self._id)
