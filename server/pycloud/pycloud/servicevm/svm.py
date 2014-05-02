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
class ServiceVM(runningvm):
    
    # Prefix used to name Service VMs.
    SERVICE_VM_INSTANCE_PREFIX = 'servicevm'

    ################################################################################################################  
    # Creates a Service VM from a Stored Service VM. If required, it starts it with a VNC GUI, and stores its state once 
    # the GUI is closed.
    # NOTE: If showVNC is True, it will show a VNC GUI and block there until the GUI is closed.
    # NOTE: If sshHostPort=None, then the VM will pick a default host port for SSH when that port is mapped.        
    ################################################################################################################         
    def createFromStoredVM(self, storedVM, vmId=None, namePrefix=None, showVNC=False, sshHostPort=None, serviceHostPort=None):
        # Check if we got a prefix, or use the default one.
        if(namePrefix == None):
            namePrefix = self.SERVICE_VM_INSTANCE_PREFIX 

        # Create the actual VM.
        super(ServiceVM, self).__init__(id = vmId,
                                        prefix = namePrefix, 
                                        diskImageFile = storedVM.diskImageFilePath)

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
    def connectToExistingVM(self, vmId, diskImageFile):
        # Create an empty VM object first.
        super(ServiceVM, self).__init__(id=vmId, diskImageFile=diskImageFile)
        
        # Try to connect to an existing running VM.
        try:
            self.connectToRunningVM()
        except runningvm.VirtualMachineException as ex:
            print 'Error connecting to existing instance: ' + str(ex)
            raise ServiceVMException('Could not connect to existing VM with id %s.' % str(vmId))        
        
