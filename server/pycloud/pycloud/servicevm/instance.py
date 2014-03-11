#!/usr/bin/env python
#       

# Used to check file existence and handle paths.
import os.path

# To delete folder contents and to move files.
import shutil

# To handle VMs.
from pycloud.pycloud.vm import runningvm

# To create Running Service VMs (from this same package).
import runningsvmfactory

# To get info about existing VMs (from this same package).
import svmrepository

################################################################################################################
# Exception type used in our system.
################################################################################################################
class ServiceVMException(Exception):
    def __init__(self, message):
        super(ServiceVMException, self).__init__(message)
        self.message = message    

################################################################################################################
# Representas a transient or temporary ServiceVM.
################################################################################################################
class ServiceVMInstance(object):
    
    # The id of this particular instance, which will be generate once it is started.
    instanceId = None
    
    # The id of the Service which this instance contains.
    serviceId = None
    
    # The external port in the host which will be mapped to the internal service port.
    serviceHostPort = None
    
    # The external port in the host which will be mapped to the internal SSH server port.
    sshHostPort = None
    
    # The path to the folder where the temporary folder for the transient VM should be stored.
    instancesRootFolder = None
    
    # The actual running VM.
    runningSVM = None
    
    ################################################################################################################
    # Constructor, recieves the Service ID, plus the external ports which will be mapped to this instance.
    ################################################################################################################
    def __init__(self, serviceId, serviceHostPort, sshHostPort, instancesRootFolder):
        self.serviceId = serviceId
        self.serviceHostPort = serviceHostPort
        self.sshHostPort = sshHostPort
        self.instancesRootFolder = instancesRootFolder        

    ################################################################################################################  
    # Gets the folder where an instance will run.
    ################################################################################################################   
    def getInstanceFolder(self):
        instanceFolder = os.path.join(self.instancesRootFolder, str(self.instanceId))
        return instanceFolder        
        
    ################################################################################################################  
    # Starts a temporary instance of a Service VM.
    ################################################################################################################   
    def createAndStart(self, showVNC=False):
        # Get information about the VM to execute.
        serviceVmRepo = svmrepository.ServiceVMRepository()
        storedServiceVM = serviceVmRepo.findServiceVM(self.serviceId)
        if(storedServiceVM == None):
            raise ServiceVMException("No valid VM for service id %s was found in the repository. " % self.serviceId)
        
        # Create a VM id for the running VM, and store it as our id.
        self.instanceId = runningvm.RunningVM.generateRandomId()
        
        # Now we create a temporary clone of the template ServiceVM, which will be our instance.
        # We don't want to store changes to the template Service VM. Therefore, we have to make a copy of the disk image and start the VM
        # with that disposable copy, in a temporary folder.
        print '\n*************************************************************************************************'        
        print "Copying Service VM files to temporary folder."
        clonedStoredVMFolderPath = os.path.join(self.instancesRootFolder, self.instanceId)
        clonedStoredServiceVM = storedServiceVM.cloneToFolder(clonedStoredVMFolderPath)        
        
        # Make the files readable and writable by all, so that libvirt can access them.
        clonedStoredServiceVM.unprotect()
        print "Service VM files copied to folder %s." % (clonedStoredServiceVM.folder)
        
        print '\n*************************************************************************************************'        
        print "Resuming VM."
        self.runningSVM = runningsvmfactory.RunningSVMFactory.createRunningVM(storedVM=clonedStoredServiceVM,
                                                                                        vmId=self.instanceId,
                                                                                        showVNC=showVNC,
                                                                                        sshHostPort=self.sshHostPort,
                                                                                        serviceHostPort=self.serviceHostPort)

        # Return our id.
        return self.instanceId
        
    ################################################################################################################  
    # Stops a running instance of a Service VM.
    ################################################################################################################  
    def stop(self):
        print "Stopping Service VM with instance id %s" % (self.instanceId)
        try:
            # Destroy the transient VM.
            print "Stopping VM with id %s" % (self.instanceId)
            self.runningSVM.destroy()
            print "VM instance with id %s was stopped and destroyed" % (self.instanceId)
        finally:
            # We get rid of the instance folder.
            instanceFolder = self.getInstanceFolder()
            if(os.path.exists(instanceFolder)):
                shutil.rmtree(instanceFolder)
                print "Temporary folder for instance of Server VM with id %s was removed" % (self.instanceId)
                
    ################################################################################################################
    # Opens an SSH session.
    ################################################################################################################       
    def openSSHConnection(self):
        self.runningSVM.openSSHConnection()        
        
    ################################################################################################################
    # Closes an SSH session.
    ################################################################################################################       
    def closeSSHConnection(self):
        self.runningSVM.closeSSHConnection()
    
    ################################################################################################################
    # Uploads a file through SFTP to a running VM.
    # NOTE: destFilePath has to be a full file path, not only a folder.
    ################################################################################################################       
    def uploadFile(self, sourceFilePath, destFilePath):
        self.runningSVM.uploadFile(sourceFilePath, destFilePath)
        
    ################################################################################################################
    # Sends a command through SSH to a running VM.
    ################################################################################################################       
    def executeCommand(self, command):       
        return self.runningSVM.executeCommand(command)
