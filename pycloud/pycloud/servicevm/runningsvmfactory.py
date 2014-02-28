#!/usr/bin/env python
#       

# To handle VMs.
import vm.runningvm

################################################################################################################
# Represents a factory to create Running Service VMs.
################################################################################################################
class RunningSVMFactory(object):
    
    # Prefix used to name Service VMs.
    SERVICE_VM_INSTANCE_PREFIX = 'servicevm'

    ################################################################################################################  
    # Creates a running VM from a stored VM. If required, it starts it with a VNC GUI, and stores its state once 
    # the GUI is closed.
    # NOTE: If showVNC is True, it will show a VNC GUI and block there until the GUI is closed.
    # NOTE: If sshHostPort=None, then the VM will pick a default host port for SSH when that port is mapped.        
    ################################################################################################################         
    @staticmethod
    def createRunningVM(storedVM, vmId=None, namePrefix=None, showVNC=False, sshHostPort=None, serviceHostPort=None):
        # Check if we got a prefix, or use the default one.
        if(namePrefix == None):
            namePrefix = RunningSVMFactory.SERVICE_VM_INSTANCE_PREFIX 

        # Create the actual VM.
        virtualMachine = vm.runningvm.RunningVM(id = vmId,
                                                prefix = namePrefix, 
                                                diskImageFile = storedVM.diskImageFilePath)

        # Add port mappings.
        virtualMachine.addForwardedSshPort(sshHostPort)
        if(serviceHostPort != None):
            # If serviceHostPort is None, it means we don't want to enable the service yet. If it is valid,
            # we will add the port mapping to enable access to the service.        
            virtualMachine.addForwardedPort(serviceHostPort, storedVM.metadata.servicePort)
        
        # Start the VM. This will block if showVNC is true.
        virtualMachine.resume(storedVM.vmStateImageFilepath, showVNC=showVNC)

        return virtualMachine
