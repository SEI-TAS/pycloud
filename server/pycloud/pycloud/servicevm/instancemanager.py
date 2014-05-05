#!/usr/bin/env python
#       

# For file handling.
import os.path

# To delete folder contents and to move files.
import shutil

# To handle the actual VMs (from this same package).
import instance
from pycloud.pycloud.servicevm import svm

# To handle ports.
from pycloud.pycloud.utils import portmanager

################################################################################################################
# Exception type used in our system.
################################################################################################################
class ServiceVMInstanceManagerException(Exception):
    def __init__(self, message):
        super(ServiceVMInstanceManagerException, self).__init__(message)
        self.message = message   

################################################################################################################
# Handles ServerVM Instances.
################################################################################################################
class ServiceVMInstanceManager(object):
    
    # Map of running VM instances, keyed by instance id.
    serviceVMInstances = {}

    # Map of list of running VM instances, stored by service id.
    runningServices = {}
    
    # Unified list of the ids of the current running instances. Used for tracking changes in the list.
    instancesIdList = '';
    
    # Timestamp of the last change.
    lastChangestamp = 0;

    ################################################################################################################  
    # Cleans up the root folder for VMs instances.
    ################################################################################################################   
    def cleanupInstancesFolder(self):
        rootInstancesFolder = self.cloudletConfig.svmInstancesFolder
        if(os.path.exists(rootInstancesFolder)):
            shutil.rmtree(rootInstancesFolder)
        if(not os.path.exists(rootInstancesFolder)):
            os.makedirs(rootInstancesFolder)  
                    
    ################################################################################################################  
    # Stops all VM instances existing in the instances folder.
    ################################################################################################################     
    def cleanupRunningInstances(self):
        # Loop over all running vms.
        print 'Attempting to clean up instances in instance folder...'
        rootInstancesFolder = self.cloudletConfig.svmInstancesFolder
        
        # Create the cache folder if it does not exist.
        if(not os.path.exists(rootInstancesFolder)):
            os.makedirs(rootInstancesFolder)        
        
        # Loop over the folders, finding valid instances.
        instancesFolderList = os.listdir(rootInstancesFolder)
        for currentFolder in instancesFolderList:
            # Only use folders.
            if(os.path.isdir(os.path.join(rootInstancesFolder, currentFolder))):
                # Assume the folder has an instance, with the id being the folder's name. 
                instanceId = currentFolder
                
                try:
                    # Try to connect to a running instance with this id.
                    svmInstance = instance.ServiceVMInstance(rootInstancesFolder)                    
                    svmInstance.connectToExistingInstance(instanceId)
                    
                    # Stop the SVM instance.
                    svmInstance.stop()                    
                except svm.ServiceVMException as exception:
                    # Could not connect to existing instance, probably folder was a leftover.
                    print 'Error stopping VM instance with id ' + instanceId + ' (probably folder had no associated VM): ' + str(exception)                
            
        print 'Instances in instance folder cleaned up.'
                    
    ################################################################################################################  
    # Stops all existing running vms.
    ################################################################################################################     
    def cleanup(self):
        # Loop over all running vms.
        print 'Cleaning up instance manager...'
        for instanceId in self.serviceVMInstances.keys():
            self.stopServiceVMInstance(instanceId)       
            
        # Clear any stored ports, if any.
        portmanager.PortManager.clearPorts()
        
        print 'Instance manager cleaned up.'
            
    ################################################################################################################  
    # Constructor.
    ################################################################################################################       
    def __init__(self, cloudletConfig):
        # Store the config object.
        self.cloudletConfig = cloudletConfig
        
        # Stop any leftover VMs from a previous session, if any.
        self.cleanupRunningInstances()
   
        # Cleanup the VMs instances folder.
        self.cleanupInstancesFolder()
        portmanager.PortManager.clearPorts()
        
    ################################################################################################################  
    # Starts an instance of a Service VM, or joins an existing one.
    ################################################################################################################   
    def getServiceVMInstance(self, serviceId, serverHostPort=None, showVNC=False, joinExisting=False):
        # By default we don't have a running instance.
        runningInstance = None
                
        # If we are allowed to use an existing instance for this service, check if there is one running.
        if(joinExisting):
            # Check if there are instances associated with the given service id.
            if((serviceId in self.runningServices) and (len(self.runningServices[serviceId]) > 0)):
                # Check the list of instances associated with this service.
                serviceIdInstances = self.runningServices[serviceId]
                print 'Running instances for service %s: %d.' % (serviceId,len(serviceIdInstances))
                for instanceId in serviceIdInstances:
                    # We will just pick the first one to use (bad load balancing...).
                    runningInstance = serviceIdInstances[instanceId]
                    break;
            
        # Check if we have to start a new transient VM.
        newInstanceNeeded = runningInstance == None
        if(newInstanceNeeded):
            runningInstance = self.__createNewInstance(serviceId, serverHostPort, showVNC)
        
        # Return the instance information.
        return runningInstance
    
    ################################################################################################################  
    # Creates a new Server VM instance, and records all pertinent information in memory so we can track it.
    ################################################################################################################  
    def __createNewInstance(self, serviceId, serviceHostPort, showVNC):
        # If no host port was provided, look for a free one.
        # This could still choose a port in use by another process.
        if(serviceHostPort == None):
            serviceHostPort = portmanager.PortManager.generateRandomAvailablePort()
            
        # Look for a free port for SSH.
        # This could still pick a port in use by another process.
        sshHostPort = portmanager.PortManager.generateRandomAvailablePort()
        
        # Start a new transient VM.
        instancesRootFolder = self.cloudletConfig.svmInstancesFolder
        serviceVMInstance = instance.ServiceVMInstance(instancesRootFolder)
        serviceVMInstance.createAndStart(self.cloudletConfig, serviceId, serviceHostPort, sshHostPort, showVNC)
    
        # Save this instance in our list of running instances.
        print "Adding to running instances list " + serviceVMInstance.instanceId
        self.serviceVMInstances[serviceVMInstance.instanceId] = serviceVMInstance
        
        # We also store these instances by Service Id, so we can easily check if a certain service has a running instance without
        # going through the whole list.
        if(not self.runningServices.has_key(serviceId)):
            self.runningServices[serviceId] = {}
        self.runningServices[serviceId][serviceVMInstance.instanceId] = serviceVMInstance
        
        return serviceVMInstance        
                            
    ################################################################################################################  
    # Stops a running instance of a Service VM.
    ################################################################################################################   
    def stopServiceVMInstance(self, instanceId):
        try:
            # Get the instance.
            serviceVMInstance = self.serviceVMInstances.pop(instanceId, None)
            
            # Check if this instance is actually running according to our records.
            if(serviceVMInstance == None):
                print('Warning: attempting to stop VM that is not registered in list of running VMs: ' + instanceId)
                return False
            else:
                # Stop the VM instance.
                serviceVMInstance.stop()
        except instance.ServiceVMException as exception:
            # Most likely VM could not be found.
            print 'Error stopping VM instance with id ' + instanceId + ': ' + str(exception)
            raise ServiceVMInstanceManagerException('Error stopping VM instance: ' + exception.message)
        finally:            
            if(serviceVMInstance != None):
                print "Cleaning up VM instance data."
                                
                # Release the ports.
                portmanager.PortManager.freePort(serviceVMInstance.serviceHostPort)      
                portmanager.PortManager.freePort(serviceVMInstance.sshHostPort)
            
                # Remove this from our list of running instances for a particular Service id.
                serviceId = serviceVMInstance.serviceId
                if(self.runningServices.has_key(serviceId)):
                    self.runningServices[serviceId].pop(instanceId, None)
                else:                
                    print "Server id entry not found while cleaning up VM instance."
                    
        return True
                    
    ################################################################################################################  
    # Returns the running Service VM instances.
    ################################################################################################################    
    def getServiceVMInstances(self):
        return self.serviceVMInstances
