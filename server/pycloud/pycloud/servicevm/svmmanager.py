#!/usr/bin/env python
#       

################################################################################################################
# Imports.
################################################################################################################

# Manager of VM stuff.
from pycloud.pycloud.vm import storedvm
import instancemanager
import svmrepository
import storedsvmfactory
import svmfactory
from pycloud.pycloud import cloudlet

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
    def createServiceVM(self, type, sourceImage, serviceId, name, port):
        try:
            # Create it.
            newStoredServiceVM = ssvmfactory.StoredServiceVMFactory.createFromDiskImage(self.cloudletConfig,
                                                                             vmType=type,
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
            
    ################################################################################################################
    # Creates and runs a transient copy of a stored service VM present in the cache for user interaction.
    ################################################################################################################
    def runServiceVMInstance(self, serviceId):
        try:   
            # Run a VM with a VNC GUI.
            instanceMan = instancemanager.ServiceVMInstanceManager(self.cloudletConfig)
            runningInstance = instanceMan.getServiceVMInstance(serviceId=serviceId,
                                                               showVNC=True)

            # After we unblocked because the user closed the GUI, we just kill the VM.
            instanceMan.stopServiceVMInstance(runningInstance.instanceId)
        except instancemanager.ServiceVMInstanceManagerException as e:
            print "Error running Service VM: " + e.message
            
    ################################################################################################################
    # Allows the modification of an existing ServiceVM from the cache.
    ################################################################################################################
    def modifyServiceVM(self, serviceId):        
        try:     
            # Get the VM, and make it writeable.
            serviceVMRepository = svmrepository.ServiceVMRepository(self.cloudletConfig)
            storedServiceVM = serviceVMRepository.getStoredServiceVM(serviceId)
            storedServiceVM.unprotect()
            
            # Run the VM with GUI and store its state.
            defaultMaintenanceServiceHostPort = 16001
            serviceVM = svmfactory.ServiceVMFactory.createServiceVM(storedVM=storedServiceVM,
                                                                             showVNC=True,
                                                                             serviceHostPort=defaultMaintenanceServiceHostPort)
            serviceVM.suspendToFile()
            
            # Destroy the service VM.
            serviceVM.destroy()     
            
            # Make the stored VM read only again.
            storedServiceVM.protect()
        except instancemanager.ServiceVMInstanceManagerException as e:
            print "Error modifying Service VM: " + e.message
            
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
        except vmrepository.VMRepositoryException as e:
            print "Error getting list of Server VMs: " + e.message
            
    ################################################################################################################
    # Tests an SSH connection to a VM.
    ################################################################################################################
    def testSSH(self, serviceId, sfilepath, dfilepath, command):
        instanceMan = None
        runningInstance = None        
        try:
            # Create the manager and access the VM.
            instanceMan = instancemanager.ServiceVMInstanceManager(self.cloudletConfig)
            runningInstance = instanceMan.getServiceVMInstance(serviceId=serviceId,
                                                               showVNC=False)
            
            # Send commands.
            runningInstance.uploadFile(sfilepath, dfilepath)
            result = runningInstance.executeCommand(command)
            print 'Result of command: ' + result
            
            # Close connection.
            runningInstance.closeSSHConnection()
            
        except instancemanager.ServiceVMInstanceManagerException as e:
            print "Error testing ssh connection: " + e.message     
        finally:
            # Cleanup.
            if(instanceMan != None and runningInstance != None):
                instanceMan.stopServiceVMInstance(runningInstance.instanceId) 

    