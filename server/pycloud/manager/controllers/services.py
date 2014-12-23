import logging
import json
import os.path

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons import g

from webhelpers.html.grid import Grid
from webhelpers.html import HTML
from webhelpers.html import literal

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.manager.lib.pages import ServicesPage
from pycloud.pycloud.pylons.lib import helpers as h
from pycloud.pycloud.model import Service

log = logging.getLogger(__name__)

################################################################################################################
# Controller for the Services page.
################################################################################################################
class ServicesController(BaseController):

    JSON_OK = json.dumps({"STATUS" : "OK" })
    JSON_NOT_OK = json.dumps({ "STATUS" : "NOT OK"})   

    ############################################################################################################
    # Entry point.
    ############################################################################################################
    def GET_index(self):
        return self.GET_listServices()

    ############################################################################################################
    # Shows the list of cached Services.
    ############################################################################################################
    def GET_listServices(self):
        # Mark the active tab.
        c.services_active = 'active'
    
        # Get a list of existing stored VMs in the cache.
        services = Service.find()
        
        # Pass the grid and render the page.
        servicesPage = ServicesPage()
        # servicesPage.servicesGrid = servicesGrid
        servicesPage.services = services

        return servicesPage.render()
        
    ############################################################################################################
    # Shows the list of cached Services.
    ############################################################################################################        
    def GET_removeService(self, id):
        try:
            service = Service.find_and_remove(id)
            if service:
                service.destroy(force=True)
        except Exception as e:
            # If there was a problem removing the service, return that there was an error.
            print 'Error removing Service: ' + str(e)
            return self.JSON_NOT_OK
        
        # Everything went well.
        return self.JSON_OK