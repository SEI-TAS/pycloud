import logging

# Pylon imports.
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

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
        self.runningVMManager = instancemanager.ServiceVMInstanceManager()

    ################################################################################################################    
    # Cleans up any open resources.
    ################################################################################################################ 
    def cleanup(self):
        # Cleanup running vms.
        if(self.runningVMManager != None):
            self.runningVMManager.cleanup()    
    
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
        serviceVmRepo = svmrepository.ServiceVMRepository()
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
        isolated = "true"
        # TODO: non-isolated
        
        # Start the Service VM on a random port.
        print '\n*************************************************************************************************'        
        timelog.TimeLog.stamp("Request received: start VM with service id " + serviceId)
        
        # Check if we will want to try to join an existing VM.
        joinIfPossible = False
        if(isolated == "false"):
            print "Will join existing VM if possible."
            joinIfPossible = True
            
        # Get our current IP, the one that the client requesting this is seeing.
        #hostIp = cherrypy.server.socket_host   #Should be cherrypy.request.local.ip, but it is not working...
        hostIp = urlparse.urlparse(request.environ['HTTP_HOST']).hostname
        
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
        # Stop the Service VM.
        instanceId = request.GET['instanceId']        
        print '\n*************************************************************************************************'
        timelog.TimeLog.reset()        
        timelog.TimeLog.stamp("Request received: stop VM with instance id " + instanceId)
        
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
