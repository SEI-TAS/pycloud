#!/usr/bin/env python
#       

# For file handling.
import os

# For configuration file management.
from pycloud.pycloud.utils import config

# To get info about existing VMs.
from pycloud.pycloud.vm import vmrepository

# To get info about existing VMs (from this same package).
import storedservicevm

################################################################################################################
# Stores information about existing ServiceVMs in the system.
################################################################################################################
class ServiceVMRepository(vmrepository.VMRepository):

    ################################################################################################################
    # Just sets up a root folder.
    ################################################################################################################    
    def __init__(self, cloudletConfig):
        repoRootFolder = cloudletConfig.svmCache
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
    # Returns a list of the VM ids and their information.
    ################################################################################################################    
    def getStoredServiceVMList(self):        
        # We will get all folders in the repo, and obtain the information form the files inside.
        vmList = {}
        vmIdList = os.listdir(self.vmRepositoryFolder)
        for vmId in vmIdList:
            try:
                # Get the current Stored SVM info.            
                storedSVM = self.getStoredServiceVM(vmId)

                # Add the id and name to the list.
                vmList[vmId] = storedSVM                
            except storedvm.StoredVMException as ex:
                print 'Ignoring invalid Stored SVM folder: %s' % vmId
        
        # Return the dictionary
        return vmList        
    
    ################################################################################################################
    # Gets information about a stored Service VM from the repository.
    ################################################################################################################
    def getStoredServiceVM(self, vmId):
        # Check if the entry exists.
        if(not self.exists(vmId)):
            raise vmrepository.VMRepositoryException("VM %s does not exist in repository." % vmId)
        
        # Create a StoredServiceVM object and return it.       
        storedVM = storedservicevm.StoredServiceVM(vmId)
        vmFolder = self.getStoredVMFolder(vmId)
        storedVM.loadFromFolder(vmFolder)
        return storedVM    
