__author__ = 'jdroot'

# Import libvirt to access the virtualization API.
import libvirt

# Used to generate unique IDs for the VMs.
from uuid import uuid4

from pycloud.pycloud.mongo import Model
from pycloud.pycloud.model.vmimage import VMImage
from pycloud.pycloud.vm.vmsavedstate import VMSavedState
from pycloud.pycloud.vm.virtualmachinedescriptor import VirtualMachineDescriptor
from pycloud.pycloud.utils import portmanager


################################################################################################################
# Exception type used in our system.
################################################################################################################
class VirtualMachineException(Exception):
    def __init__(self, message):
        super(VirtualMachineException, self).__init__(message)
        self.message = message


class ServiceVM(Model):
    class Meta:
        collection = "service_vms"
        external = ['_id', 'service_id', 'running', 'port']
        mapping = {
            'vm_image': VMImage
        }

    # URI used to connect to the local hypervisor.
    _HYPERVISOR_URI = "qemu:///session"
    _hypervisor = None

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
    # Generates a random ID, valid as a VM id.
    ################################################################################################################
    def generate_random_id(self):
        self._id = str(uuid4())

    ################################################################################################################
    # Start this service vm
    ################################################################################################################
    def start(self):
        # Make sure libvirt can read our files
        self.vm_image.unprotect()

        print 'vm_image.state_image = ', self.vm_image.state_image

        # Get the saved state and make sure it is populated
        if not self.vm_image.state_image:
            pass  # TODO: self.vm_image.state_image = self.getDefaultSavedStateFile()
        saved_state = VMSavedState(self.vm_image.state_image)

        # Get the descriptor and inflate it to something we can work with
        saved_xml_descriptor = saved_state.getStoredVmDescription(ServiceVM.get_hypervisor())
        xml_descriptor = VirtualMachineDescriptor(saved_xml_descriptor)

        # Set the disk image in the description of the VM.
        xml_descriptor.setDiskImage(self.vm_image.disk_image, 'qcow2')

        # Set up the port mappings
        self.port = portmanager.PortManager.generateRandomAvailablePort()
        if not self.port_mappings:  # Create a blank dict if the port mappings are empty (shouldn't happen)
            self.port_mappings = {}
        self.port_mappings[self.service_port] = self.port
        xml_descriptor.setPortRedirection(self.port_mappings)

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

