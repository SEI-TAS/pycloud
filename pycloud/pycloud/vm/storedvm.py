#!/usr/bin/env python
#       

# Used to check file existence and handle paths.
import os.path

# Used to copy files.
import shutil

# Used to change file permissions.
import stat

# To handle disk images.
import vm.diskimage

# Used to handle data about saved state files.
import vm.vmsavedstate

# Used to create a VM with our stored files.
import vm.runningvm

# File utils.
import utils.fileutils

################################################################################################################
# Exception type used in this module.
################################################################################################################
class StoredVMException(Exception):
    def __init__(self, message):
        super(StoredVMException, self).__init__(message)
        self.message = message    

################################################################################################################
# An object that represents a stored VM. A Stored VM consists of a disk image file and a saved state file.
################################################################################################################
class StoredVM(object):
    
    # Identifier of the stored VM.
    id = None
    
    # The folder where the files are stored.
    folder = None
    
    # The disk image of this stored VM.
    diskImageFilePath = None
    
    # The saved sate of this stored VM.
    vmStateImageFilepath = None
    
    # The name of the files, without extensions, is used a a short "name" of the Stored VM.
    name = None
    
    ################################################################################################################
    # Constructor.
    ################################################################################################################    
    def __init__(self, newId):
        # Set basic data.
        self.id = newId
        
    ################################################################################################################
    # Loads information about the VM from the files that are in its folder.
    ################################################################################################################          
    def loadFromFolder(self, vmFolder):
        # Check that the folder actually exists.        
        if(not os.path.exists(vmFolder)):
            raise StoredVMException("Folder %s for VM does not exist." % vmFolder)
        self.folder = vmFolder
        
        # Loop over the files in the folder, finding valid image files.
        vmFileList = os.listdir(vmFolder)
        for currentFilename in vmFileList:
            # Check for disk image file.
            if(vm.diskimage.DiskImage.isValidDiskImageFilename(currentFilename)):
                self.diskImageFilePath = os.path.join(vmFolder, currentFilename)
                 
                # We use the name of this file, without its extensions, as a simple name for the stored VM.
                fileParts = os.path.splitext(currentFilename)
                self.name = fileParts[0]
                 
            # Check for VM saved state image file.
            if(vm.vmsavedstate.VMSavedState.isValidSavedStateFilename(currentFilename)):
                self.vmStateImageFilepath = os.path.join(vmFolder, currentFilename)

        # If we didn't find a disk or saved state image, there is something seriously wrong.
        if(self.diskImageFilePath == None or self.vmStateImageFilepath == None):
            raise StoredVMException("VM in folder %s did not contain a valid disk or saved state image." % vmFolder)
        
    ################################################################################################################
    # Moves the VM files of an existing VM entry into a new folder.
    ################################################################################################################             
    def moveToFolder(self, destinationFolderPath):
        # First clear the folder and ensure it is there.
        utils.fileutils.FileUtils.recreateFolder(destinationFolderPath)
        
        # Go through all the files in our folder.
        vmFileList = os.listdir(self.folder)
        for currentFilename in vmFileList:
                # Now actually move it.
                currentFilePath = os.path.join(self.folder, currentFilename)
                if os.path.isfile(currentFilePath):
                    shutil.move(currentFilePath, destinationFolderPath)
            
        # Now reload our information, since we moved.
        self.loadFromFolder(destinationFolderPath)            
        
    ################################################################################################################
    # Protects a Stored VM by making it read-only.
    ################################################################################################################         
    def protect(self):        
        # Go through all the files in our folder.
        vmFileList = os.listdir(self.folder)
        for currentFilename in vmFileList:
            # Marks a file as read only.
            currentFilePath = os.path.join(self.folder, currentFilename)
            if os.path.isfile(currentFilePath):
                os.chmod(currentFilePath, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        
    ################################################################################################################
    # Makes the files of a Store VM available (read and write) to all.
    ################################################################################################################         
    def unprotect(self):
        # Go through all the files in our folder.
        vmFileList = os.listdir(self.folder)
        for currentFilename in vmFileList:
            # Make it readable and writeable to all users.
            currentFilePath = os.path.join(self.folder, currentFilename)
            if os.path.isfile(currentFilePath):            
                os.chmod(currentFilePath, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH | stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
