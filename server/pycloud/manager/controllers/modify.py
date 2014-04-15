import logging
import os
import json
import urllib

from pylons import request, response, session, tmpl_context as c, url
from pylons import g
from pylons.templating import render_mako as render

from webhelpers.html import HTML

from pycloud.pycloud.servicevm import svmrepository
from pycloud.pycloud.servicevm import svmmanager
from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.pycloud.pylons.lib import helpers as h

from pycloud.manager.lib.pages import ModifyPage

log = logging.getLogger(__name__)

################################################################################################################
# Controller for the Modify page.
################################################################################################################
class ModifyController(BaseController):

    JSON_OK = json.dumps({"STATUS" : "OK" })
    JSON_NOT_OK = json.dumps({ "STATUS" : "NOT OK"})

    ################################################################################################################ 
    #
    ################################################################################################################ 
    def GET_index(self):
        # Mark the active tab.
        c.services_active = 'active'
                
        # Load the data into the page.
        page = ModifyPage()        
        serviceID = request.params.get("serviceId")
        page.serviceID = serviceID
        page = self.loadDataIntoPage(page, serviceID)

        # Render the page with the data.
        return page.render()
    
    ################################################################################################################ 
    # Loads data about the stored service vm into a page, and returns the filled page.
    ################################################################################################################         
    def loadDataIntoPage(self, page, serviceID):
        # Setup the page to render.
        page.form_values = {}
        page.form_errors = {}
        page.storedSvmButtonHtml = ''
        page.initScript = ''
                
        # Check if we are editing or creating a new service.
        creatingNew = serviceID is None
        if(creatingNew):
            # We are creating a new service.
            page.newService = True
            
            # URL to create a new Service VM.
            page.createSVMURL =  h.url_for(controller="modify", action='createSVM')
        else:
            # We are editing an existing service.
            page.newService = False
                        
            # Get the data fields.
            serviceID = serviceID.strip()
            serviceVmRepo = svmrepository.ServiceVMRepository(g.cloudlet)
            storedServiceVM = serviceVmRepo.findServiceVM(serviceID)
            
            # Add link to open an SVM.
            page.openSVMURL = h.url_for(controller="modify", action='openSVM', id=serviceID)
            
            # Set the data fields.
            page.form_values['serviceID'] = serviceID
            if (storedServiceVM is not None):
                # Metadata values.
                page.form_values['servicePort'] = storedServiceVM.metadata.servicePort
            
                # Stored SVM values.
                page.form_values['vmStoredFolder'] = os.path.dirname(storedServiceVM.diskImageFilePath)
                page.form_values['vmDiskImageFile'] = storedServiceVM.diskImageFilePath
                page.form_values['vmStateImageFile'] = storedServiceVM.vmStateImageFilepath

        return page

    ################################################################################################################ 
    # Modifying a Service record.
    ################################################################################################################         
    def POST_index(self):
        # Mark the active tab.
        c.services_active = 'active'
        
        # Service
        serviceID           = request.params.get("serviceID")
        serviceVersion      = request.params.get("serviceVersion")
        serviceDescription  = request.params.get("serviceDescription")
        serviceTags         = request.params.get("serviceTags")
        servicePort         = request.params.get("servicePort")

        # App
        appName             = request.params.get("appName")
        appDescription      = request.params.get("appDescription")
        appVersion          = request.params.get("appVersion")
        appPackage          = request.params.get("appPackage")
        appFilename         = request.params.get("appFilename")

        # VM
        vmStoredFolder      = request.params.get("vmStoredFolder")

        # Requirements
        reqMinMem           = request.params.get("reqMinMem")
        reqIdealMem         = request.params.get("reqIdealMem")

        print serviceID + ": " + serviceDescription + ": " + reqMinMem
        
        # Load the current Stored SVM info.
        # Note that we have to use the original service id to find the data, 
        # since it may have been changed by the user.
        originalServiceID = request.params.get("originalServiceID")
        serviceVmRepo = svmrepository.ServiceVMRepository(g.cloudlet)
        storedServiceVM = serviceVmRepo.findServiceVM(originalServiceID)

        # Change the values.
        storedServiceVM.metadata.serviceId = serviceID
        storedServiceVM.metadata.servicePort = servicePort
        
        # Store them back to file.
        storedServiceVM.unprotect()
        storedServiceVM.metadata.writeToFile(storedServiceVM.metadataFilePath)
        storedServiceVM.protect()
        
        # If the service ID changed, rename the folders (as it needs to have the correct id).
        if(originalServiceID != serviceID):
            serviceVmRepo.renameStoredVM(originalServiceID, serviceID)
        
        # Load the data into the page.
        page = ModifyPage()
        page.serviceID = serviceID
        page = self.loadDataIntoPage(page, serviceID)
        
        # Add a notification to the user about the changes.
        page.initScript = 'document.getElementsByTagName("body")[0].addEventListener("load", showEditSuccess, false);';
        
        # Render the page.
        return page.render()

    ############################################################################################################
    # Creates a new Service VM and opents it in a VNC window for editing.
    # NOTE: The VNC window will only open on the computer running the server.
    ############################################################################################################
    def POST_createSVM(self):
        # Get the manager.
        print 'Creating SVM...'
        svmManager = svmmanager.ServiceVMManager(g.cloudlet)
        
        # Parse the body of the request as JSON into a python object.
        print request.body
        parsedJsonString = urllib.unquote(request.body)[:-1]
        print parsedJsonString
        fields = json.loads(parsedJsonString)        
        
        # Create an SVM and open a VNC window to modify the VM.
        svmManager.createServiceVM(osType = fields['type'], 
                                   sourceImage = fields['source'],
                                   serviceId = fields['serviceId'], 
                                   name = fields['serviceId'],
                                   port = fields['port'])
        
        # Everything went well.
        return self.JSON_OK

    ############################################################################################################
    # Opens the Service VM in a VNC window for editing.
    # NOTE: The VNC window will only open on the computer running the server.
    ############################################################################################################
    def GET_openSVM(self, id):
        # Get the manager.
        svmManager = svmmanager.ServiceVMManager(g.cloudlet)
        
        # Open a VNC window to modify the VM.
        svmManager.modifyServiceVM(id)
        
        # Everything went well.
        return self.JSON_OK    
 