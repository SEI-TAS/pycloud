#!/usr/bin/env python
#       

# To handle VMs.
from pycloud.pycloud.vm import runningvm

################################################################################################################
# Exception type used in our system.
################################################################################################################
class ServiceVMException(Exception):
    def __init__(self, message):
        super(ServiceVMException, self).__init__(message)
        self.message = message    

################################################################################################################
# Represents Service VMs.
################################################################################################################
class ServiceVM(runningvm.RunningVM):   
    # Prefix used to name Service VMs.
    SERVICE_VM_PREFIX = 'servicevm'
    
    ################################################################################################################  
    # Basic constructor, usually received a disk image file associated with this VM.
    ################################################################################################################         
    def __init__(self, vmId = None, prefix = None, diskImageFile = None):
        # Set default prefix if necessary.
        if(prefix == None):
            prefix = self.SERVICE_VM_PREFIX
            
        # Call the base constructor.
        super(ServiceVM, self).__init__(id = vmId, prefix = prefix, diskImageFile = diskImageFile)    
              
    ################################################################################################################  
    # Starts a Service VM from a source disk image and XML descriptor. This is done when creating a new Service VM
    # from scratch and loading it up with its components.
    ################################################################################################################         
    def startFromDescriptor(self, xmlVmDescriptionFilepath, showVNC=False):               
        # Add the default port.
        self.addForwardedSshPort()
        
        # Start te VM with the given descriptor
        self.start(xmlVmDescriptionFilepath, showVNC=showVNC)

    ################################################################################################################  
    # Creates a Service VM from a Stored Service VM. If required, it starts it with a VNC GUI, and stores its state once 
    # the GUI is closed.
    # NOTE: If showVNC is True, it will show a VNC GUI and block there until the GUI is closed.
    # NOTE: If sshHostPort=None, then the VM will pick a default host port for SSH when that port is mapped.        
    ################################################################################################################         
    def startFromStoredSVM(self, storedVM, showVNC=False, sshHostPort=None, serviceHostPort=None):
        # Setup the disk image to point to the stored VM disk image.
        self.setDiskImage(storedVM.diskImageFilePath)
        
        # Add port mappings.
        self.addForwardedSshPort(sshHostPort)
        if(serviceHostPort != None):
            # If serviceHostPort is None, it means we don't want to enable the service yet. If it is valid,
            # we will add the port mapping to enable access to the service.        
            self.addForwardedPort(serviceHostPort, storedVM.metadata.servicePort)
        
        # Start the VM. This will block if showVNC is true.
        self.resume(storedVM.vmStateImageFilepath, showVNC=showVNC)
        
    ################################################################################################################  
    # Sets up the Service VM as a connection from a running VM (and its associated disk file).
    ################################################################################################################         
    def connectToRunningVM(self):
        # Try to connect to an existing running VM.
        try:
            super(ServiceVM, self).connectToRunningVM()
        except runningvm.VirtualMachineException as ex:
            print 'Error connecting to existing Service VM: ' + str(ex)
            raise ServiceVMException('Could not connect to existing Service VM with id %s.' % str(self.id))
