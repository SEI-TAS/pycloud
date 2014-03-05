#!/usr/bin/env python
#       

# Used to check file existence and handle paths.
import os.path

# Used to copy files.
import shutil

# Used to represent stored VM info (from this same package)
import storedvm

################################################################################################################
# Exception type used in our system.
################################################################################################################
class VMRepositoryException(Exception):
    def __init__(self, message):
        super(VMRepositoryException, self).__init__(message)
        self.message = message    

################################################################################################################
# Handles a repository of VMs.
################################################################################################################
class VMRepository(object):
    
    # Root folder for the VMs.
    vmRepositoryFolder = None

    ################################################################################################################
    # Returns the complete path of the folder where a StoredVM is/would-be stored.
    # It will be inside the given root folder, in a folder named after the ID of the VM.
    ################################################################################################################    
    def getStoredVMFolder(self, vmId):
        vmFolder = os.path.join(self.vmRepositoryFolder, vmId)
        return vmFolder

    ################################################################################################################
    # Just sets up a root folder.
    ################################################################################################################    
    def __init__(self, rootFolder):
        self.vmRepositoryFolder = rootFolder

    ################################################################################################################
    # Returns a list of the VM ids and their information.
    ################################################################################################################    
    def getVMList(self):        
        # We will get all folders in the repo, and obtain the information form the files inside.
        vmList = {}
        vmIdList = os.listdir(self.vmRepositoryFolder)
        for vmId in vmIdList:
            # Get the current Stored VM info.
            try:
                storedVM = self.getStoredVM(vmId)

                # Add the id and name to the list.
                vmList[vmId] = storedVM                
            except storedvm.StoredVMException as ex:
                print 'Ignoring invalid Stored VM folder: %s' % vmId
        
        # Return the dictionary
        return vmList
    
    ################################################################################################################
    # Gets a string with a list of VMs.
    ################################################################################################################    
    def getVMListAsString(self):
        # Header for printout.
        vmListString =  '----------------------------------------------------------------\n'
        vmListString += 'ID\t\t\t\t\tName\n'
        vmListString += '----------------------------------------------------------------\n'
        
        # Get the list of VMs.        
        vmList = self.getVMList()                
        for vmId in vmList.keys():
            vmListString += vmId + '\t\t' + vmList[vmId].name + '\n'
        
        # Simply return the string.
        return vmListString       

    ################################################################################################################
    # Checks if a given VM is stored.
    ################################################################################################################        
    def exists(self, vmId):
        # For now we just check if there is a folder for this VM.
        vmFolder = self.getStoredVMFolder(vmId)
        return os.path.exists(vmFolder)
      
    ################################################################################################################
    # Gets information about a VM from the repository.
    ################################################################################################################
    def getStoredVM(self, vmId):
        # Check if the entry exists.
        if(not self.exists(vmId)):
            raise VMRepositoryException("VM %s does not exist in repository." % vmId)
        
        # Create a VMInfo object and return it.       
        storedVM = storedvm.StoredVM(vmId)
        vmFolder = self.getStoredVMFolder(vmId)
        storedVM.loadFromFolder(vmFolder)
        return storedVM

    ################################################################################################################
    # Removes an entry from the repository.
    ################################################################################################################        
    def deleteStoredVM(self, vmId):
        # Clear everything up from the VM folder.
        vmFolder = self.getStoredVMFolder(vmId)
        if(os.path.exists(vmFolder)):
            shutil.rmtree(os.path.join(vmFolder))
            
    ################################################################################################################
    # Adds an entry to the repository. It will overwrite an existing one with the same id, if any.
    ################################################################################################################        
    def addStoredVM(self, storedVM):
        # Delete the Stored VM, if there was one with the same id.
        if(self.exists(storedVM.id)):
            self.deleteStoredVM(storedVM.id)

        # Create the VM folder.
        vmFolder = self.getStoredVMFolder(storedVM.id)
        os.makedirs(vmFolder)      
        
        # Copy the files that come with this VM into the repository.
        storedVM.moveToFolder(vmFolder)
        
        # Protect the stored VM from accidental deletion.
        storedVM.protect()
