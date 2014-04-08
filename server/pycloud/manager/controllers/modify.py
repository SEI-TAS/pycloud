import logging
import os
import json

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

        # Setup the page to render.
        page = ModifyPage()
        page.form_values = {}
        page.form_errors = {}
        page.modifyButtonHtml = ''
                
        # Get the data fields.
        serviceID = request.params.get("serviceId")
        if(serviceID is not None):
            serviceID = serviceID.strip()
            serviceVmRepo = svmrepository.ServiceVMRepository(g.cloudlet)
            storedServiceVM = serviceVmRepo.findServiceVM(serviceID)
            
            # Add link to open an SVM.
            openSVMURL = h.url_for(controller="modify", action='openSVM', id=serviceID)
            page.modifyButtonHtml = HTML.button("Modify SVM", onclick=h.literal("openEditVNC('"+ openSVMURL +"')"), class_="btn btn-primary btn", type="button")
            
            # Set the data fields.
            page.form_values['serviceID'] = serviceID
            if (storedServiceVM is not None):
                page.form_values['vmStoredFolder'] = os.path.dirname(storedServiceVM.diskImageFilePath)
                page.form_values['vmDiskImageFile'] = storedServiceVM.diskImageFilePath
                page.form_values['vmStateImageFile'] = storedServiceVM.vmStateImageFilepath

        # Render the page with the grid.
        return page.render()

    ################################################################################################################ 
    #
    ################################################################################################################         
    def POST_index(self):
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
        vmDiskImageFile     = request.params.get("vmDiskImageFile")
        vmStateImageFile    = request.params.get("vmStateImageFile")

        # Requirements
        reqMinMem           = request.params.get("reqMinMem")
        reqIdealMem         = request.params.get("reqIdealMem")

        print serviceID + ": " + serviceDescription + ": " + reqMinMem
        
        page = ModifyPage()
        page.form_values = {}
        page.form_errors = {}
        page.modifyButtonHtml = ''
        
        return page.render()

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
 