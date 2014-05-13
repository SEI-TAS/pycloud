__author__ = 'jdroot'

# Import libvirt to access the virtualization API.
import libvirt

# Used to generate unique IDs for the VMs.
from uuid import uuid4

from pycloud.pycloud.mongo import Model
from pycloud.pycloud.model.vmimage import VMImage
from pycloud.pycloud.vm.vmsavedstate import VMSavedState
from pycloud.pycloud.vm.virtualmachinedescriptor import VirtualMachineDescriptor
from pycloud.pycloud.vm.vncclient import VNCClient
from pycloud.pycloud.utils import portmanager
from pylons import g
import os


################################################################################################################
# Exception type used in our system.
################################################################################################################
class VirtualMachineException(Exception):
    def __init__(self, message):
        super(VirtualMachineException, self).__init__(message)
        self.message = message

################################################################################################################
# Represents a runtime ServiceVM, idependent on whether it has a cloned or original disk image.
################################################################################################################
class ServiceVM(Model):
    # Meta class is needed so that minimongo can map this class onto the database.
    class Meta:
        collection = "service_vms"
        external = ['_id', 'service_id', 'running', 'port']
        mapping = {
            'vm_image': VMImage
        }

    # URI used to connect to the local hypervisor.
    _HYPERVISOR_URI = "qemu:///session"
    _hypervisor = None

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
        self.service_id = None
        self.running = False
        super(ServiceVM, self).__init__(*args, **kwargs)

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
    # Add a port mapping
    ################################################################################################################
    def add_port_mapping(self, host_port, guest_port):
        if not self.port_mappings:
            self.port_mappings = {}

        # If you are setting the services port we need to set the external port in a particular attribute.
        if guest_port == self.service_port:
            self.port = host_port   

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
    # Start this service vm
    ################################################################################################################
    def start(self):
        # Make sure libvirt can read our files
        self.vm_image.unprotect()

        # Get the saved state and make sure it is populated
        if not self.vm_image.state_image:
            pass  # TODO: self.vm_image.state_image = self.getDefaultSavedStateFile()
        saved_state = VMSavedState(self.vm_image.state_image)

        # Get the descriptor and inflate it to something we can work with
        saved_xml_descriptor = saved_state.getStoredVmDescription(ServiceVM.get_hypervisor())
        xml_descriptor = VirtualMachineDescriptor(saved_xml_descriptor)

        # Set the disk image in the description of the VM.
        xml_descriptor.setDiskImage(self.vm_image.disk_image, 'qcow2')

        # Create a new port if we do not have an external port already
        if not self.port:
            self.add_port_mapping(portmanager.PortManager.generateRandomAvailablePort(), self.service_port)
        xml_descriptor.setPortRedirection(self._get_libvirt_port_mappings())

        # Change the ID and Name
        xml_descriptor.setUuid(self._id)
        xml_descriptor.setName(self.prefix + '-' + self._id)

        # Get the resulting XML string and save it
        updated_xml_descriptor = xml_descriptor.getAsString()
        saved_state.updateStoredVmDescription(updated_xml_descriptor)

        # Restore a VM to the state indicated in the associated memory image file, in running mode.
        # The XML descriptor is given since some things have changed, though effectively it is not used here since
        # the memory image file has already been merged with this in the statement above.
        try:
            print "Resuming from VM image..."
            ServiceVM.get_hypervisor().restoreFlags(saved_state.savedStateFilename, updated_xml_descriptor, libvirt.VIR_DOMAIN_SAVE_RUNNING)
        except libvirt.libvirtError as e:
            message = "Error resuming VM: %s for VM; error is: %s" % (str(self._id), str(e))
            raise VirtualMachineException(message)

        self.running = True

        return self

    ################################################################################################################
    # Starts a VNC connection with a GUI, and, if given in the argument, waits until it is closed.
    ################################################################################################################            
    def open_vnc(self, wait=True):
        # We have to get the XML description of the running machine to find the port available for VNC.
        vm_xml_string = ServiceVM._get_virtual_machine(self._id).XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE)
        xml_descriptor = VirtualMachineDescriptor(vm_xml_string)
        
        # We can now get the VNC port, which was automatically allocated by libvirt/qemu.
        vnc_port = xml_descriptor.getVNCPort()
        
        # Connect through the VNC client and wait if required.
        print 'Starting VNC GUI to VM.'
        if wait:
            print 'Waiting for user to close VNC GUI.'
        vnc_client = VNCClient()
        success = vnc_client.connectAndWait(vnc_port, wait)
        if wait:
            print 'VNC GUI no longer running, stopped waiting.'
        else:
            print 'VNC GUI has been opened.'
            
        # If there was a problem, destroy the VM.
        if not success:
            self.destroy()

    ################################################################################################################
    # Stop this service VM
    ################################################################################################################
    def stop(self):
        # Check if this instance is actually running
        if not self.running:
            return

        print "Stopping Service VM with instance id %s" % self._id

        # TODO: self.closeSSHConnection()

        vm = ServiceVM._get_virtual_machine(self._id)
        if not vm:  # No VM for this ID found
            return

        try:
            vm.destroy()
        finally:
            self.running = False

    ################################################################################################################
    # Will delete this VM (and stop it if it is currently running)
    ################################################################################################################
    def destroy(self):
        if self.running:
            self.stop()
        self.vm_image.cleanup(os.path.join(g.cloudlet.svm_temp_folder, self._id))
        ServiceVM.find_and_remove(self._id)
