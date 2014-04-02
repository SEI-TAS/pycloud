import logging

# Pylon imports.
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons import g

# For serializing JSON data.
import json

# Controller to derive from.
from pycloud.pycloud.pylons.lib.base import BaseController

# Repository to look for SVMs, and logging util.
from pycloud.pycloud.servicevm import svmrepository
from pycloud.pycloud.utils import timelog

log = logging.getLogger(__name__)

################################################################################################################
# Class that handles Service related HTTP requests to a Cloudlet.
################################################################################################################
class ServicesController(BaseController):
    
    JSON_OK = json.dumps({"STATUS" : "OK" })
    JSON_NOT_OK = json.dumps({ "STATUS" : "NOT OK"})    
            
    ################################################################################################################
    # Get a list of the services in the VM. In realiy, for now at least, it actually get a list of services that
    # have associated ServiceVMs in the cache.
    ################################################################################################################
    def GET_list(self):
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
