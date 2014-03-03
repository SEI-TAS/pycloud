#!/usr/bin/env python
#       

# Used to check file existence and handle paths.
import os.path

# To handle VMs.
import pycloud.vm.runningvm

# Metadata about a Service VM (from this same package).
import svmmetadata

# For disk image management.
import pycloud.vm.qcowdiskimage

# Config pycloud.utils.
import pycloud.utils.config

# File pycloud.utils.
import pycloud.utils.fileutils

################################################################################################################
# Creates StoredServiceVMs.
################################################################################################################
class StoredServiceVMFactory(object):

    # Name of the configuration section for this class's parameters.    
    CONFIG_SECTION = 'servicevm'

    # Param name for configuration of overlay folder, where they will be created.
    SERVICE_VM_FOLDER_KEY = 'service_vm_creation_folder'
    
    # Param name for configuration of XML template used to create VMs.
    SOURCE_CONFIG_SECTION = 'sourceimages'    
    BASE_VM_LIN_XML_TEMPLATE_KEY = 'base_vm_lin_xml_template'    
    BASE_VM_WIN_XML_TEMPLATE_KEY = 'base_vm_win_xml_template'
    
    ################################################################################################################  
    # Method to simply getting configuration values for this module.
    ################################################################################################################       
    @staticmethod
    def __getLocalConfigParam(key):
        return pycloud.utils.config.Configuration.getParam(StoredServiceVMFactory.CONFIG_SECTION, key)
    
    ################################################################################################################  
    # Method to simply getting configuration values for this module.
    ################################################################################################################       
    @staticmethod
    def __getSourceConfigParam(key):
        return pycloud.utils.config.Configuration.getParam(StoredServiceVMFactory.SOURCE_CONFIG_SECTION, key)    
    
    ################################################################################################################
    # Creates a StoredVM from a source file.
    ################################################################################################################ 
    @staticmethod
    def createFromDiskImage(vmType, sourceDiskImageFilePath, serviceId, serviceVMName, servicePort):
        # Get the XML descriptor from the config.
        if(vmType == 'Windows'):
            xmlVmDescriptionFilepath = os.path.abspath(StoredServiceVMFactory.__getSourceConfigParam(StoredServiceVMFactory.BASE_VM_WIN_XML_TEMPLATE_KEY))
        else:
            xmlVmDescriptionFilepath = os.path.abspath(StoredServiceVMFactory.__getSourceConfigParam(StoredServiceVMFactory.BASE_VM_LIN_XML_TEMPLATE_KEY))
        
        # Ensure that the base folder is there.
        serviceVMFolder = StoredServiceVMFactory.__getLocalConfigParam(StoredServiceVMFactory.SERVICE_VM_FOLDER_KEY)
        pycloud.utils.fileutils.FileUtils.recreateFolder(serviceVMFolder)
                        
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
        sourceDiskImage = pycloud.vm.diskimage.DiskImage(sourceDiskImageFilePath)
        newDiskImageFilePath = os.path.join(serviceVMFolder, serviceVMName)
        newDiskImage = pycloud.vm.qcowdiskimage.Qcow2DiskImage(newDiskImageFilePath)
        newDiskImage.createFromOtherType(sourceDiskImage)
        
        # We start the VM and load a GUI so the user can modify it. We block till he finished. In this process the user
        # will convert the contents of this VM into an actual Service VM by loading it with the appropriate server.
        print "Loading VM for user access..."
        virtualMachine = pycloud.vm.runningvm.RunningVM(diskImageFile = newDiskImage.filepath)
        virtualMachine.addForwardedSshPort()
        virtualMachine.start(xmlVmDescriptionFilepath, showVNC=True)
        virtualMachine.suspendToFile()
        print "Service VM stopped, and machine state saved."

        # Load our data from the folder where we just put everything into.
        storedServiceVM = storedservicevm.StoredServiceVM(serviceId=serviceId)   
        storedServiceVM.loadFromFolder(serviceVMFolder)
        
        # Return it.
        return storedServiceVM

