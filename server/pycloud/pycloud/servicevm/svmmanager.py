#!/usr/bin/env python
#       

################################################################################################################
# Imports.
################################################################################################################

# Manager of VM stuff.
from pycloud.pycloud.vm import storedvm
import svmrepository
import storedsvmfactory
import svm

# For exceptions.
from pycloud.pycloud.vm import vmrepository
  
################################################################################################################
# Handles ServiceVMs in the local cache.
################################################################################################################
class ServiceVMManager(object):

    cloudletConfig = None

    ################################################################################################################  
    # Constructor.
    ################################################################################################################       
    def __init__(self, cloudletConfig):
        # Store the config object.
        self.cloudletConfig = cloudletConfig

    ################################################################################################################
    # Creates and a new Service VM into the cache.
    ################################################################################################################
    def createServiceVM(self, osType, sourceImage, serviceId, name, port):
        try:
            # Create it.
            newStoredServiceVM = storedsvmfactory.StoredServiceVMFactory.createFromDiskImage(self.cloudletConfig,
                                                                             vmType=osType,
                                                                             sourceDiskImageFilePath=sourceImage,
                                                                             serviceId=serviceId, 
                                                                             serviceVMName=name, 
                                                                             servicePort=port)
            
            # Store it in the repo.
            print "Saving ServiceVM."
            serviceVMRepository = svmrepository.ServiceVMRepository(self.cloudletConfig)
            serviceVMRepository.addStoredVM(newStoredServiceVM)
            print "ServiceVM stored in repository."            
            
        except storedvm.StoredVMException as e:
            print "Error creating Service VM: " + e.message 
            return None
        
        return newStoredServiceVM
            
    ################################################################################################################
    # Allows the modification of an existing Stored ServiceVM from the cache.
    ################################################################################################################
    def modifyServiceVM(self, serviceId):        
        try:     
            # Get the VM, and make it writeable.
            serviceVMRepository = svmrepository.ServiceVMRepository(self.cloudletConfig)
            storedServiceVM = serviceVMRepository.getStoredServiceVM(serviceId)
            storedServiceVM.unprotect()
            
            # Run the VM with GUI and store its state.
            defaultMaintenanceServiceHostPort = 16001
            serviceVM = svm.ServiceVM()
            serviceVM.startFromStoredSVM(storedVM=storedServiceVM,
                                         showVNC=True,
                                         serviceHostPort=defaultMaintenanceServiceHostPort)
            serviceVM.suspendToFile()
            print 'Service VM stored.'
            
            # Destroy the service VM.
            serviceVM.destroy()     
            
            # Make the stored VM read only again.
            storedServiceVM.protect()
            
            return True
        except Exception as e:
            print "Error modifying Service VM: " + e.message
            return False
            
    ################################################################################################################
    # Prints a list of Service VMs in the cache.
    ################################################################################################################
    def listServiceVMs(self):
        try:
            # Get a list and print it.
            serviceVmRepo = svmrepository.ServiceVMRepository(self.cloudletConfig)
            vmList = serviceVmRepo.getVMListAsString()
            print '\nService VM List:'
            print vmList
            return True
        except vmrepository.VMRepositoryException as e:
            print "Error getting list of Server VMs: " + e.message
            return False
    