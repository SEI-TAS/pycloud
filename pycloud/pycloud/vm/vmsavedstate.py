#!/usr/bin/env python
#       

# Used to handle paths more easily.
import os.path

# Used to modify UUID of a saved VM.
import vmnetx
        
################################################################################################################
# Represents a saved image of a VM state, including a memory image.
################################################################################################################
class VMSavedState(object):
    
    # Extension for memory files. Since now we are using Libvirt Qemu Save images, we will use the lqs extension.
    SAVED_VM_FILE_EXTENSION = '.lqs'    
    
    ################################################################################################################
    # Sets up internal values of the VM state image.
    ################################################################################################################        
    def __init__(self, savedStateFile):        
        # Store the name of the file associated with our state.
        self.savedStateFilename = VMSavedState.getCorrectFilepath(savedStateFile)
        
    ################################################################################################################
    # Returns the default filename for the saved state of a VM, which is based on the given path.
    ################################################################################################################     
    @staticmethod 
    def getDefaultSavedStateFile(filepath):
        return VMSavedState.getCorrectFilepath(filepath)        
        
    ################################################################################################################
    # Returns the default filename
    ################################################################################################################
    @staticmethod     
    def getCorrectFilepath(filepath):
        # Ensure that the file ends with the correct extension.
        savedStateFilepath = filepath
        if(not VMSavedState.isValidSavedStateFilename(filepath)):
            savedStateFilepath += VMSavedState.SAVED_VM_FILE_EXTENSION
        return savedStateFilepath         
            
    ################################################################################################################
    # Checks if a given filename is a valid saved state file, by checking the extension only.
    ################################################################################################################ 
    @staticmethod                  
    def isValidSavedStateFilename(filepath):            
        # Check that the extension is the expected one.
        fileExtension = os.path.splitext(filepath)[1] 
        isValid = fileExtension == VMSavedState.SAVED_VM_FILE_EXTENSION
        return isValid    
        
    ################################################################################################################
    # Checks if the image file actually exists.
    ################################################################################################################          
    def exists(self):
        return os.path.exists(self.savedStateFilename)
    
    ################################################################################################################
    # Returns the XMl description of the VM from a saved state file.
    ################################################################################################################       
    def getStoredVmDescription(self, hypervisor):
        xmlDescription = hypervisor.saveImageGetXMLDesc(self.savedStateFilename, 0)
        return xmlDescription
    
    ################################################################################################################
    # Returns the XMl description of the VM from a saved state file, raw format.
    ################################################################################################################       
    def getRawStoredVmDescription(self, hypervisor):
        with open(self.savedStateFilename, 'r') as savedStateFileStream:
            hdr = vmnetx.LibvirtQemuMemoryHeader(savedStateFileStream)
            return hdr.xml
    
    ################################################################################################################
    # Modifies the given image/VM state file to store an update XML. Required to change things like UUID.
    ################################################################################################################  
    def updateStoredVmDescription(self, newXmlDescriptorString):
        with open(self.savedStateFilename, 'r+') as savedStateFileStream:
            # First we load the header with the VM description to memory.
            hdr = vmnetx.LibvirtQemuMemoryHeader(savedStateFileStream)
            
            # Then we replace the XML portion of the header with the new description, storing it back to the saved state file.
            #print('\nOriginal:' + hdr.xml + '\n')
            #print('\nNew:' + newXmlDescriptorString + '\n')
            hdr.xml = newXmlDescriptorString
            hdr.write(savedStateFileStream)
            