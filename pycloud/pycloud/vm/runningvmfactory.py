#!/usr/bin/env python
#       

# To handle VMs.
import vm.runningvm

################################################################################################################
# Represents a factory to create running VMs.
################################################################################################################
class RunningVMFactory(object):

    ################################################################################################################  
    # Creates a running VM from a stored VM. If required, it starts it with a VNC GUI.
    # NOTE: If showVNC is True, it will show a VNC GUI and block there until the GUI is closed.
    # NOTE: If sshHostPort=None, then the VM will pick a default host port for SSH when that port is mapped.        
    ################################################################################################################         
    @staticmethod
    def createRunningVM(self, storedVM, vmId=None, namePrefix=None, showVNC=False, sshHostPort=None):
        # Create the actual VM.
        virtualMachine = vm.runningvm.RunningVM(id = vmId,
                                                                prefix = namePrefix, 
                                                                diskImageFile = storedVM.diskImageFilePath)

        # Add port mappings.
        virtualMachine.addForwardedSshPort(sshHostPort)
        
        # Start the VM. This will block if showVNC is true.
        virtualMachine.resume(storedVM.vmStateImageFilepath, showVNC=showVNC)

        return virtualMachine
