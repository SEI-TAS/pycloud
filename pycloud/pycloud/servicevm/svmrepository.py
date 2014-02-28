#!/usr/bin/env python
#       

# For configuration file management.
import utils.config

# To get info about existing VMs.
import vm.vmrepository

# To get info about existing VMs.
import servicevm.storedservicevm

################################################################################################################
# Stores information about existing ServiceVMs in the system.
################################################################################################################
class ServiceVMRepository(vm.vmrepository.VMRepository):
    
    # Name of the configuration section for this class's parameters.    
    CONFIG_SECTION = 'servicevm'
    
    # Param name for configuration of root folder for Service VMs.
    SERVER_VM_FOLDER_KEY = 'service_vm_repository'

    ################################################################################################################  
    # Method to simply getting configuration values for this module.
    ################################################################################################################       
    def __getLocalConfigParam(self, key):
        return utils.config.Configuration.getParam(self.CONFIG_SECTION, key)    

    ################################################################################################################
    # Just sets up a root folder.
    ################################################################################################################    
    def __init__(self):
        repoRootFolder = self.__getLocalConfigParam(self.SERVER_VM_FOLDER_KEY)
        super(ServiceVMRepository, self).__init__(repoRootFolder)
    
    ################################################################################################################  
    # Checks if a given server VM exists on the repository. Returns a VMEntry to the VM that was found, or None if it was not found.
    ################################################################################################################   
    def findServiceVM(self, serviceVmId):
        # Get information about the VM.
        print '\n*************************************************************************************************'        
        print "Finding Service VM."              
        if(self.exists(serviceVmId)):
            storedVM = self.getStoredServiceVM(serviceVmId)
        else:
            # This exception will only occur if the VM does not exist. We just return None in this case.
            print "VM with id %s was not found." % (serviceVmId)
            return None

        # Check that we were able to get metadata.
        if(storedVM.metadata == None):
            # The Service VM is not valid... equivalent to no VM.
            print "No metadata file for Service VM %s " % serviceVmId
            return None       

        print "Service VM found."
        return storedVM
    
    ################################################################################################################
    # Gets information about a stored Service VM from the repository.
    ################################################################################################################
    def getStoredServiceVM(self, vmId):
        # Check if the entry exists.
        if(not self.exists(vmId)):
            raise vm.vmrepository.VMRepositoryException("VM %s does not exist in repository." % vmId)
        
        # Create a VMInfo object and return it.       
        storedVM = servicevm.storedservicevm.StoredServiceVM(vmId)
        vmFolder = self.getStoredVMFolder(vmId)
        storedVM.loadFromFolder(vmFolder)
        return storedVM    
