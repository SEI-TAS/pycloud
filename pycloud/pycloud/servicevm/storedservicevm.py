#!/usr/bin/env python
#       

# Used to check file existence and handle paths.
import os.path

# To delete folder contents and to move files.
import shutil

# Base class of a generic stored VM.
from pycloud.pycloud.vm import storedvm

# Metadata about a Service VM (from this same package).
import svmmetadata

# For disk image management.
from pycloud.pycloud.vm import qcowdiskimage

# File utils.
from pycloud.pycloud.utils import fileutils

################################################################################################################
# An object that represents a stored Service VM.
################################################################################################################
class StoredServiceVM(storedvm.StoredVM):

    # ServiceVM metadata file.
    metadataFilePath = None
    
    # The loaded contents of the ServiceVM metadata file.
    metadata = None
    
    ################################################################################################################
    # Constructor.
    # Note that for ServiceVMs, the vmId is the Service ID.
    ################################################################################################################    
    def __init__(self, serviceId):
        super(StoredServiceVM, self).__init__(serviceId)
        
    ################################################################################################################
    # @Override
    # Loads information about the VM from the files that are in its folder.
    ################################################################################################################          
    def loadFromFolder(self, vmFolder):
        # Call the base loader.
        super(StoredServiceVM, self).loadFromFolder(vmFolder)        
        
        # Loop over the files in the folder, finding valid metadata files.
        vmFileList = os.listdir(vmFolder)
        for currentFilename in vmFileList:
            # Check if there is a metadata file, if so, load it into memory. This will only be there for Server VMs.
            if(svmmetadata.ServiceVMMetadata.isValidMetadataFilename(currentFilename)):
                self.metadataFilePath = os.path.join(vmFolder, currentFilename)
                self.metadata = svmmetadata.ServiceVMMetadata()
                self.metadata.loadFromFile(self.metadataFilePath)                 

        # If we didn't find a disk or saved state image, there is something seriously wrong.
        if(self.metadataFilePath == None):
            raise storedvm.StoredVMException("VM in folder %s did not contain a valid metadata file." % vmFolder)
        
    ################################################################################################################
    # Creates a clone of a StoredServiceVM.
    ################################################################################################################
    def cloneToFolder(self, clonedStoredVMFolderPath):
        # Create the folder for these files.
        fileutils.FileUtils.recreateFolder(clonedStoredVMFolderPath)
        
        # Copy the files.
        shutil.copy(self.vmStateImageFilepath, clonedStoredVMFolderPath)
        shutil.copy(self.metadataFilePath, clonedStoredVMFolderPath)
        
        if(self.metadata.refImageId == 'None'):
            # For the disk image, create a shallow qcow2 file pointing at the original image, instead of copying it, for faster startup.
            clonedFilepath = os.path.join(clonedStoredVMFolderPath, self.name)
            clonedDiskImage = qcowdiskimage.Qcow2DiskImage(clonedFilepath)
            clonedDiskImage.linkToBackingFile(self.diskImageFilePath)
        else:
            # If we are using a synthesized VM with a disk image pointing at a base disk image, libvirt won't allow double redirection, 
            # so we have to copy the disk image instead.
            shutil.copy(self.diskImageFilePath, clonedStoredVMFolderPath)

        # Load the file paths and metadata from the new, cloned location.
        clonedStoredServiceVM = StoredServiceVM(self.id)        
        clonedStoredServiceVM.loadFromFolder(clonedStoredVMFolderPath)
        
        # Finally return the object pointing to the cloned stored Service VM.
        return clonedStoredServiceVM
