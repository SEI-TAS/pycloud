#!/usr/bin/env python
#       

# Used to check file existence and handle paths.
import os.path

# To handle VMs.
from pycloud.pycloud.servicevm import svm

# Metadata about a Service VM (from this same package).
import svmmetadata

import storedservicevm

# For disk image management.
from pycloud.pycloud.vm import diskimage
from pycloud.pycloud.vm import qcowdiskimage

# File utils.
from pycloud.pycloud.utils import fileutils

################################################################################################################
# Creates StoredServiceVMs.
################################################################################################################
class StoredServiceVMFactory(object):
    
    ################################################################################################################
    # Creates a StoredVM from a source file.
    ################################################################################################################ 
    @staticmethod
    def createFromDiskImage(cloudletConfig, vmType, sourceDiskImageFilePath, serviceId, serviceVMName, servicePort):
        # Get the XML descriptor from the config.
        if(vmType == 'Windows'):
            xmlVmDescriptionFilepath = os.path.abspath(cloudletConfig.newVmWinXml)
        else:
            xmlVmDescriptionFilepath = os.path.abspath(cloudletConfig.newVmLinXml)
        
        # Ensure that the base folder is there.
        serviceVMFolder = cloudletConfig.newVmFolder
        fileutils.FileUtils.recreateFolder(serviceVMFolder)
                        
        # Now we create the metadata file about the ServiceVM.
        print "Creating Service VM metadata file."
        serviceVMMetadata = svmmetadata.ServiceVMMetadata()
        serviceVMMetadata.serviceId = serviceId
        serviceVMMetadata.servicePort = servicePort
        serviceVMMetadata.writeToFile(os.path.join(serviceVMFolder, serviceVMName))
        print "Metadata file created."
        
        # Create a new disk image for the Service VM, from the source image.
        # The call to "clone" will add the appropriate extension, so we can use the service name as the filename.
        print "Service VM disk image creation step."
        sourceDiskImage = diskimage.DiskImage(sourceDiskImageFilePath)
        newDiskImageFilePath = os.path.join(serviceVMFolder, serviceVMName)
        newDiskImage = qcowdiskimage.Qcow2DiskImage(newDiskImageFilePath)
        newDiskImage.createFromOtherType(sourceDiskImage)
        
        # We start the VM and load a GUI so the user can modify it. We block till he finished. In this process the user
        # will convert the contents of this VM into an actual Service VM by loading it with the appropriate server.
        print "Loading VM for user access..."
        serviceVM = svm.ServiceVM(diskImageFile = newDiskImage.filepath)
        serviceVM.startFromDescriptor(xmlVmDescriptionFilepath=xmlVmDescriptionFilepath, showVNC=True)
        print "VNC GUI closed, saving machine state..."
        serviceVM.suspendToFile()
        print "Service VM stopped, and machine state saved."

        # Load our data from the folder where we just put everything into.
        storedServiceVM = storedservicevm.StoredServiceVM(serviceId=serviceId)   
        storedServiceVM.loadFromFolder(serviceVMFolder)
        
        # Return it.
        return storedServiceVM

