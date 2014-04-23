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

# Manager to handle running instances, and logging util.
from pycloud.pycloud.servicevm import instancemanager
from pycloud.pycloud.utils import timelog
from pycloud.pycloud.pylons.lib.util import asjson

log = logging.getLogger(__name__)

################################################################################################################
# Class that handles Service VM related HTTP requests to a Cloudlet.
################################################################################################################
class ServiceVMController(BaseController):
    
    # Manager of service VMs instances.
    instanceManager = None
    
    JSON_OK = json.dumps({"STATUS" : "OK" })
    JSON_NOT_OK = json.dumps({ "STATUS" : "NOT OK"})    

    ################################################################################################################    
    # Sets up the initial resources.
    ################################################################################################################ 
    def __init__(self):
        # Create the manager for running instances.
        self.instanceManager = g.cloudlet.instanceManager

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
    @asjson
    def GET_listServices(self):
        print '\n*************************************************************************************************'
        timelog.TimeLog.reset()
        timelog.TimeLog.stamp("Request received: get list of Services.")
        
        # Get the list of stored service vms in the cache.
        serviceVmCache = svmrepository.ServiceVMRepository(g.cloudlet)
        vmList = serviceVmCache.getStoredServiceVMList()

        # Create an item list with the info to display.
        servicesList = []
    	for storedVMId in vmList:
            storedVM = vmList[storedVMId]
            serviceInfo = {'_id': storedVM.metadata.serviceId,
                           'description': storedVM.name}
            servicesList.append(serviceInfo)        
        
        # Create a JSON response to indicate the result.
        jsonDataStructure = {"services": servicesList}
        
        # Send the response.
        timelog.TimeLog.stamp("Sending response back to " + request.environ['REMOTE_ADDR'])
        return jsonDataStructure
            
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
        serviceVmRepo = svmrepository.ServiceVMRepository(g.cloudlet)
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
        # Start the Service VM on a random port.
        print '\n*************************************************************************************************'        

        # Get variables.
        serviceId = request.GET['serviceId']
        if(serviceId is None):
            # If we didnt get a valid one, just return an error message.
            print "No service id to be started was received."
            return self.JSON_NOT_OK

        timelog.TimeLog.stamp("Request received: start VM with service id " + serviceId)

        # Check the flags that indicates whether we could join an existing instance.
        isolated = request.params.get('isolated', True)
        if not isinstance(isolated, bool): # Will only be bool if it was none and the default was set
            isolated = isolated.lower() in ("yes", "true", "t", "1")

        
        # Start the Service VM on a random port.
        print '\n*************************************************************************************************'        
        timelog.TimeLog.stamp("Request received: start VM with service id " + serviceId)
        
        # Check if we will want to try to join an existing VM.
        joinIfPossible = not isolated
        if joinIfPossible:
            print "Will join existing VM if possible."

        # Get our current IP, the one that the client requesting this is seeing.
        # The HTTP_HOST header will also have the port after a colon, so we remove it.
        hostIp = request.environ['HTTP_HOST'].split(':')[0]

        # Start or join a VM.
        instanceInfo = self.instanceManager.getServiceVMInstance(serviceId=serviceId, joinExisting=joinIfPossible)
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
            return self.JSON_NOT_OK

        print '\n*************************************************************************************************'
        timelog.TimeLog.reset()        
        timelog.TimeLog.stamp("Request received: stop VM with instance id " + instanceId)
        
        # Stop the Service VM.        
        success = self.instanceManager.stopServiceVMInstance(instanceId)
        if(success):
            print "VM with instance id %s stopped" % instanceId
            responseText = self.JSON_OK
        else:
            print "VM with instance id %s could not be stopped" % instanceId
            responseText = self.JSON_NOT_OK
        
        # Send the response.
        timelog.TimeLog.stamp("Sending response back to " + request.environ['REMOTE_ADDR'])
        timelog.TimeLog.writeToFile()
        return responseText
