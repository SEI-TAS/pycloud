#!/usr/bin/env python
#       

# Used to copy files.
import shutil

# Used to check file existence.
import os.path

# To create unique IDs from hashes.
import hashlib

# To show progerss visually, for hash calculation.
from pycloud.pycloud.utils import progressbar

################################################################################################################
# Exception type used in our system.
################################################################################################################
class DiskImageException(Exception):
    def __init__(self, message):
        super(DiskImageException, self).__init__(message)
        self.message = message    

################################################################################################################
# Simple structure to represent a disk image.
################################################################################################################
class DiskImage(object):

    # Describes the image types that the class knows how to handle.
    # This is not the best way to handle this, as new types will require changes to this class (ie, adding them to this list).
    TYPE_RAW = 'raw'
    TYPE_QCOW2 = 'qcow2'
    SUPPORTED_IMAGE_TYPES = ( TYPE_RAW, TYPE_QCOW2 )
    
    ################################################################################################################
    # Sets up internal values of the disk image.
    # This will NOT create an actual disk image file, it will only create the DiskImage object.
    ################################################################################################################        
    def __init__(self, diskImageFilepath):
        # Try to automatically guess the image type form extension.
        diskImageType = DiskImage.getDiskImageType(diskImageFilepath)
        if(diskImageType == None):
            # If we couldn't get it, throw an error.
            raise DiskImageException("Filepath %s contains no extension, so image type can not be obtained." % diskImageFilepath)
        
        # Check that the image type is valid.
        if(not DiskImage.isValidDiskImageType(diskImageType)):
            raise DiskImageException("Disk image type " + diskImageType + " not supported.")
        
        # Set the basic characteristics of a disk image.
        self.filepath = diskImageFilepath
        self.type = diskImageType
            
    ################################################################################################################
    # Returns the type of a given file (basically its extension), or None if it had no extension.
    ################################################################################################################ 
    @staticmethod                  
    def getDiskImageType(diskImageFilepath):
        # This splits the extension and puts it in the second location of the array.
        diskImageExtension = os.path.splitext(diskImageFilepath)[1]
        
        # Check if we got an extension.
        if(diskImageExtension != ''):
            # Remove the '.' before returning the type.
            diskImageType = diskImageExtension[1:]
            
            # Check if this extension is a valid type.
            if(DiskImage.isValidDiskImageType(diskImageType)):
                return diskImageType
            else:
                return None
        else:
            return None
            
    ################################################################################################################
    # Checks if a given filename is a valid disk image.
    ################################################################################################################ 
    @staticmethod                  
    def isValidDiskImageFilename(diskImageFilepath):            
        # Check that we support this image type.
        diskImageType = DiskImage.getDiskImageType(diskImageFilepath)
        isValid = DiskImage.isValidDiskImageType(diskImageType)
        return isValid
    
    ################################################################################################################
    # Checks if a given type is a valid disk type.
    ################################################################################################################ 
    @staticmethod                  
    def isValidDiskImageType(imageType):            
        # Check that we support this image type.
        isValid = imageType in DiskImage.SUPPORTED_IMAGE_TYPES
        return isValid    

    ################################################################################################################
    #  Copies a disk image file into a new location, and returns a new DiskImage object pointing to that location.
    ################################################################################################################  
    def clone(self, cloneDiskImageFilepath):
        # Check if the source disk image file exists.
        if not os.path.exists(self.filepath):
            raise DiskImageException("Source image file does not exist (%s)." % self.filepath)
                
        # Check if the new disk image file already exists.
        if os.path.exists(cloneDiskImageFilepath):
            # This is an error, as we don't want to overwrite an existing disk image with a source.
            raise DiskImageException("Destination image file already exists (%s). Will not overwrite existing image." % cloneDiskImageFilepath)
        
        # Check if the filepath has a valid extension, and add if it not.
        if(not DiskImage.isValidDiskImageFilename(cloneDiskImageFilepath)):
            extension = '.' + self.type
            cloneDiskImageFilepath = cloneDiskImageFilepath + extension
        
        # Simply copy the file.  
        print "Copying disk image %s to new disk image %s..." % (self.filepath, cloneDiskImageFilepath)
        shutil.copyfile(self.filepath, cloneDiskImageFilepath)        
        print 'Disk image copied.'
        
        # Create the cloned object.
        clonedDiskImage = DiskImage(cloneDiskImageFilepath)
        return clonedDiskImage
          
    ################################################################################################################
    # Calculates an unique ID for the image file.
    ################################################################################################################ 
    @staticmethod  
    def calculateId(imageFilepath):
        return DiskImage.__calculateFileHash(imageFilepath)
    
    ################################################################################################################
    # Calculates the MD5 hash of a file without loading it completely into memory.
    ################################################################################################################
    @staticmethod
    def __calculateFileHash(inputFilename, blockSize=2**20):
        print "Calculating hash for file %s" % inputFilename        
        
        # Create a simple progress bar to show progress of calculated hash.
        numIterations = os.path.getsize(inputFilename) / blockSize
        progressBar = progressbar.LoopAnimatedProgressBar(end=100, width=80, numberOfIterations=numIterations)        
        
        # Loop over the file to calculate the hash incrementally.
        currIteration = 0        
        with open(inputFilename, 'rb') as inputFile:   
            hashCalculator = hashlib.md5()
            while True:
                # Update the progress bar, if required.
                progressBar.update(currIteration)
                currIteration += 1
                
                # Get a data chunk (window) and add it to the hash calculation.
                data = inputFile.read(blockSize)
                if not data:
                    break
                hashCalculator.update(data)
                
            # Once we finished reading all the file, get the readable hash from the calculator.
            print ''    # Just to ensure next prints will start in a new line.
            hashValue = str(hashCalculator.hexdigest()) 
                
        print "Hash result for file %s: %s" % (inputFilename, hashValue)                  
        return hashValue                        
        
################################################################################################################
# Functions to test the class.
################################################################################################################

################################################################################################################
# Get the command line arguments.
################################################################################################################
import argparse
def get_args():
    parser = argparse.ArgumentParser(description='Manage a disk image.')
    parser.add_argument('-diskImageFilepath', required=True, action='store',  help='The disk image path.')
    parser.add_argument('-sourceDiskImageFilepath', required=True, action='store',  help='The source disk image path.')
    parsedArguments = parser.parse_args()
    return parsedArguments

################################################################################################################
# Command line test
################################################################################################################
def testDiskImage():  
    parsedArguments = get_args()
    
    print 'Starting Disk Image test...'
    
    dm = DiskImage(parsedArguments.diskImageFilepath)
    dm.clone(parsedArguments.sourceDiskImageFilepath)
    
    print 'Test finished'

