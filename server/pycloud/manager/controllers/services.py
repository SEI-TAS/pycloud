import logging

from pylons import request, response, session, tmpl_context as c, url

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.manager.lib.pages import ServicesPage
from pycloud.pycloud.model import Service

from pycloud.pycloud.utils import ajaxutils
from pycloud.pycloud.pylons.lib.util import asjson

log = logging.getLogger(__name__)

################################################################################################################
# Controller for the Services page.
################################################################################################################
class ServicesController(BaseController):

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
    @asjson
    def GET_removeService(self, id):
        try:
            service = Service.find_and_remove(id)
            if service:
                service.destroy(force=True)
        except Exception as e:
            # If there was a problem removing the service, return that there was an error.
            msg = 'Error removing Service: ' + str(e)
            return ajaxutils.show_and_return_error_dict(msg)
        
        # Everything went well.
        return ajaxutils.JSON_OK