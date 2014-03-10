import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from pycloud.manager.lib.base import BaseController

from pycloud.pycloud.servicevm import svmrepository
from pycloud.pycloud.utils import timelog

# For serializing JSON data.
import json

log = logging.getLogger(__name__)

class ServiceVMController(BaseController):

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


