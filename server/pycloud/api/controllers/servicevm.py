import logging

# Pylon imports.
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons import g

# For serializing JSON data.
import json

# To get our IP.
import urlparse

# Controller to derive from.
from pycloud.pycloud.pylons.lib.base import BaseController

# Repository to look for SVMs, and manager to handle running instances.
from pycloud.pycloud.servicevm import svmrepository
from pycloud.pycloud.servicevm import instancemanager

from pycloud.pycloud.utils import timelog

log = logging.getLogger(__name__)

################################################################################################################
# Class that handles Service VM related HTTP requests to a Cloudlet.
################################################################################################################
class ServiceVMController(BaseController):
    
    # Manager of running VMs.
    runningVMManager = None

    ################################################################################################################    
    # Sets up the initial resources.
    ################################################################################################################ 
    def __init__(self):
        # Create the manager for running instances.        
        self.runningVMManager = instancemanager.ServiceVMInstanceManager(g.cloudlet)

    ################################################################################################################    
    # Cleans up any open resources.
    ################################################################################################################ 
    def cleanup(self):
        # Cleanup running vms.
        if(self.runningVMManager != None):
            self.runningVMManager.cleanup()
            
    ################################################################################################################
    # Get a list of the services in the VM. In realiy, for now at least, it actually get a list of services that
    # have associated ServiceVMs in the cache.
    ################################################################################################################
    def GET_listServices(self):
        print '\n*************************************************************************************************'
        timelog.TimeLog.reset()
        timelog.TimeLog.stamp("Request received: get list of Services.")
        
        # Get the list of stored service vms in the cache.
        serviceVmCache = svmrepository.ServiceVMRepository(self.cloudlet)
        vmList = serviceVmCache.getStoredServiceVMList()

        # Create an item list with the info to display.
        servicesList = []
    	for storedVMId in vmList:
            storedVM = vmList[storedVMId]
            serviceInfo = {'_id':storedVM.metadata.serviceId,
                           'description':storedVM.name}
            servicesList.append(serviceInfo)        
        
        # Create a JSON response to indicate the result.
        jsonDataStructure = { "services" : servicesList }
        jsonDataString = json.dumps(jsonDataStructure)
        
        # Send the response.
        timelog.TimeLog.stamp("Sending response back to " + request.environ['REMOTE_ADDR'])
        responseText = jsonDataString
        return responseText  
            
    ################################################################################################################
    # Called to check if a specific service is already provided by a cached Service VM on this server.
    ################################################################################################################
    def GET_find(self):
        # Look for the VM in the repository.
        serviceId = request.GET['serviceId']
        vmFound = False
        print '\n*************************************************************************************************'
        timelog.TimeLog.reset()
        timelog.TimeLog.stamp("Request received: find cached Service VM.")
        serviceVmRepo = svmrepository.ServiceVMRepository(self.cloudlet)
        vmEntry = serviceVmRepo.findServiceVM(serviceId)
        if(vmEntry != None):
            vmFound = True
        
        # Create a JSON response to indicate the result.
        jsonDataStructure = { "VM_EXISTS" : str(vmFound)
                            }
        jsonDataString = json.dumps(jsonDataStructure)
        
        # Send the response.
        timelog.TimeLog.stamp("Sending response back to " + request.environ['REMOTE_ADDR'])
        responseText = jsonDataString
        return responseText          
        
    ################################################################################################################
    # Called to start a Service VM.
    # - isolated: indicates if we want to run our own Service VM (true) or if we can share an existing one ("false")
    ################################################################################################################
    def GET_start(self):
        # Get variables.
        serviceId = request.GET['serviceId']
        if(serviceId is None):
            # If we didnt get a valid one, just return an error message.
            print "No service id to be started was received."
            responseText = 'NOT OK'
            return responseText        

        # Check the flags that indicates whether we could join an existing instance.
        isolated = request.GET['serviceId']
        if(isolated is None):
            # If no value was sent, set true by default.
            isolated = "true"
        
        # Start the Service VM on a random port.
        print '\n*************************************************************************************************'        
        timelog.TimeLog.stamp("Request received: start VM with service id " + serviceId)
        
        # Check if we will want to try to join an existing VM.
        joinIfPossible = False
        if(isolated == "false"):
            print "Will join existing VM if possible."
            joinIfPossible = True
            
        # Get our current IP, the one that the client requesting this is seeing.
        # The HTTP_HOST header will also have the port after a colon, so we remove it.
        hostIp = request.environ['HTTP_HOST'].split(':')[0]

        # Start or join a VM.
        instanceInfo = self.runningVMManager.getServiceVMInstance(serviceId=serviceId, joinExisting=joinIfPossible)
        print "Assigned VM running with id %s on IP '%s' and port %d" % (instanceInfo.instanceId, hostIp, instanceInfo.serviceHostPort)
                
        # Create a JSON response to indicate the IP and port of the Service VM (the IP will be the same as the hosts's as
        # it is using port forwarding, and the host port is the one returned by the VMM which configured the forwarding.        
        jsonDataStructure = { "IP_ADDRESS" : hostIp, \
                              "PORT" : instanceInfo.serviceHostPort, \
                              "INSTANCE_ID" : instanceInfo.instanceId
                            }
        jsonDataString = json.dumps(jsonDataStructure)
        print "Service VM Info: IP: %s, port: %s, instance id: %s" % (hostIp, str(instanceInfo.serviceHostPort), instanceInfo.instanceId)
        
        # Send the response.
        timelog.TimeLog.stamp("Sending response back to " + request.environ['REMOTE_ADDR'])
        timelog.TimeLog.writeToFile()
        responseText = jsonDataString
        return responseText
    
    ################################################################################################################
    # Called to stop a running instance of a Service VM.
    ################################################################################################################
    def GET_stop(self):
        # Check that we got an instance id.
        instanceId = request.GET['instanceId']
        if(instanceId is None):
            # If we didnt get a valid one, just return an error message.
            print "No instance id to be stopped was received."
            responseText = 'NOT OK'
            return responseText

        print '\n*************************************************************************************************'
        timelog.TimeLog.reset()        
        timelog.TimeLog.stamp("Request received: stop VM with instance id " + instanceId)
        
        # Stop the Service VM.        
        success = self.runningVMManager.stopServiceVMInstance(instanceId)
        if(success):
            print "VM with instance id %s stopped" % instanceId
            responseText = 'OK'
        else:
            print "VM with instance id %s could not be stopped" % instanceId
            responseText = 'NOT OK'
        
        # Send the response.
        timelog.TimeLog.stamp("Sending response back to " + request.environ['REMOTE_ADDR'])
        timelog.TimeLog.writeToFile()
        return responseText
