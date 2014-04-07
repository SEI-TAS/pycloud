import logging

from pycloud.pycloud.servicevm import svmrepository
from pycloud.manager.lib.pages import ServiceVMsPage

from pylons import request, response, session, tmpl_context as c, url
from pylons import g
from pylons.templating import render_mako as render

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.manager.lib.pages import ModifyPage

log = logging.getLogger(__name__)


################################################################################################################
# Controller for the Modify page.
################################################################################################################
class ModifyController(BaseController):

    def GET_index(self):
        # Mark the active tab.
        c.services_active = 'active'

        # Get the data fields.
        serviceID = request.params.get("serviceId")
        serviceVmRepo = svmrepository.ServiceVMRepository(g.cloudlet)
        storedServiceVM = serviceVmRepo.findServiceVM(serviceID)

        page = ModifyPage()
        page.form_values = {}
        page.form_errors = {}

        # Set the data fields
        page.form_values['serviceID'] = serviceID
        if (not storedServiceVM is None):
            page.form_values['vmStoredFolder'] = storedServiceVM.metadataFilePath
            page.form_values['vmStoredFolder'] = storedServiceVM.diskImageFilePath
            page.form_values['vmStateImageFile'] = storedServiceVM.vmStateImageFilepath


        # Render the page with the grid.
        return page.render()

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
        return ModifyPage().render()