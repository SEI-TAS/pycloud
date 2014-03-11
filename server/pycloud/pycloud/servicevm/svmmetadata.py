#!/usr/bin/env python
#  

# For serializing JSON data.
import json

# Used to join paths.
import os.path

################################################################################################################
# Exception type used in our system.
################################################################################################################
class SVMMetadataException(Exception):
    def __init__(self, message):
        super(SVMMetadataException, self).__init__(message)
        self.message = message    

################################################################################################################
# Represents the metadata for a Service VM.
################################################################################################################
class ServiceVMMetadata(object):

    # The service id and port.    
    serviceId = None
    servicePort = None
    
    # Optional, the id of a disk image which is a linked base for the disk image of the ServiceVM (ie, backing file for qcow2).
    refImageId = 'None'
    
    # Encoding used with metadata files.
    METADATA_FILE_CHAR_ENCODING = "UTF-8"
    
    # Extension for metadata files.
    METADATA_FILE_EXTENSION = ".jsonsvm"
    
    # String keys used in the JSON format to refer to metadata values.
    JSON_KEY_SERVICE_VM_DATA  = 'serviceVMData'          # Name for the whole section that includes the values below.
    JSON_KEY_SERVICE_ID = 'serviceId'                    # Used to identify the service provided by the ServiceVM, in Java inverse URL format.
    JSON_KEY_SERVICE_PORT = 'servicePort'                # Used to connect to the sever inside the Service VM.
    JSON_KEY_REF_IMAGE_ID = 'refImageId'                 # Optional, the id of another disk image which is must be linked as a base for our disk image.
            
    ################################################################################################################
    # Checks if a given filename is a valid metadata file.
    ################################################################################################################ 
    @staticmethod                  
    def isValidMetadataFilename(filepath):            
        # Check that the extension is the expected one.
        fileExtension = os.path.splitext(filepath)[1] 
        isValid = fileExtension == ServiceVMMetadata.METADATA_FILE_EXTENSION
        return isValid    
    
    ################################################################################################################
    # Loads metadata from a JSON file into this object.
    ################################################################################################################      
    def loadFromFile(self, filePath):        
        # Load the JSON data from the file.
        jsonData = ''
        try:
            jsonData = json.load(open(filePath, 'r'), self.METADATA_FILE_CHAR_ENCODING)
        except ValueError:
            raise SVMMetadataException("Invalid JSON format content: " + open(filePath, 'r').read())
        
        # Store it internally.
        self.toMemberFields(jsonData)

    ################################################################################################################        
    # # Just store the JSON data in member fields.
    ################################################################################################################        
    def toMemberFields(self, jsonData):
        # Check if the json data has the main group key.
        if(not self.JSON_KEY_SERVICE_VM_DATA in jsonData):
            raise SVMMetadataException("Invalid JSON content, '" + self.JSON_KEY_SERVICE_VM_DATA + "' key is missing.")
        
        # Get the data.
        self.serviceId = jsonData[self.JSON_KEY_SERVICE_VM_DATA][self.JSON_KEY_SERVICE_ID]
        self.servicePort = jsonData[self.JSON_KEY_SERVICE_VM_DATA][self.JSON_KEY_SERVICE_PORT]
        self.refImageId = jsonData[self.JSON_KEY_SERVICE_VM_DATA][self.JSON_KEY_REF_IMAGE_ID]
    
    ################################################################################################################
    # Writes metadata from this object into a JSON file.
    ################################################################################################################      
    def writeToFile(self, filePath):
        # Add the required extension if it is not there.
        if(not ServiceVMMetadata.isValidMetadataFilename(filePath)):
            filePath = filePath + self.METADATA_FILE_EXTENSION
        
        # Move the metdata into a list/dictionary, and turn it into a JSON string.
        jsonDataStructure = self.toDataStructure()        
        jsonDataString = json.dumps(jsonDataStructure)
        
        # Write the string to the default file.
        with open(filePath, 'w') as outputFile:
            outputFile.write(jsonDataString)
            
        # Since the filename may have been modified to add the extension, we return the final filepath used.
        return filePath            
        
    ################################################################################################################        
    # Moves the metdata into a list/dictionary.
    ################################################################################################################        
    def toDataStructure(self):        
        jsonDataStructure = { self.JSON_KEY_SERVICE_VM_DATA :
                                 { self.JSON_KEY_SERVICE_ID : self.serviceId, \
                                   self.JSON_KEY_SERVICE_PORT : self.servicePort, \
                                   self.JSON_KEY_REF_IMAGE_ID : self.refImageId 
                                 } 
                            }
        return jsonDataStructure

    ################################################################################################################        
    # Clones th object.
    ################################################################################################################        
    def clone(self):
        clonedSvmMetadata = ServiceVMMetadata()
        clonedSvmMetadata.serviceId = self.serviceId
        clonedSvmMetadata.servicePort = self.port
        clonedSvmMetadata.refImageId = self.refImageId
        return clonedSvmMetadata

