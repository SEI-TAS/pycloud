# KVM-based Discoverable Cloudlet (KD-Cloudlet) 
# Copyright (c) 2015 Carnegie Mellon University.
# All Rights Reserved.
# 
# THIS SOFTWARE IS PROVIDED "AS IS," WITH NO WARRANTIES WHATSOEVER. CARNEGIE MELLON UNIVERSITY EXPRESSLY DISCLAIMS TO THE FULLEST EXTENT PERMITTEDBY LAW ALL EXPRESS, IMPLIED, AND STATUTORY WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT OF PROPRIETARY RIGHTS.
# 
# Released under a modified BSD license, please see license.txt for full terms.
# DM-0002138
# 
# KD-Cloudlet includes and/or makes use of the following Third-Party Software subject to their own licenses:
# MiniMongo
# Copyright (c) 2010-2014, Steve Lacy 
# All rights reserved. Released under BSD license.
# https://github.com/MiniMongo/minimongo/blob/master/LICENSE
# 
# Bootstrap
# Copyright (c) 2011-2015 Twitter, Inc.
# Released under the MIT License
# https://github.com/twbs/bootstrap/blob/master/LICENSE
# 
# jQuery JavaScript Library v1.11.0
# http://jquery.com/
# Includes Sizzle.js
# http://sizzlejs.com/
# Copyright 2005, 2014 jQuery Foundation, Inc. and other contributors
# Released under the MIT license
# http://jquery.org/license

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
            