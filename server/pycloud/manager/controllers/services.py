import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons import g

from webhelpers.html.grid import Grid
from webhelpers.html import HTML

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.pycloud.servicevm import svmrepository
from pycloud.manager.lib.pages import ServicesPage
import pycloud.pycloud.pylons.lib.helpers as h

log = logging.getLogger(__name__)

################################################################################################################
# Controller for the Services page.
################################################################################################################
class ServicesController(BaseController):

    ############################################################################################################
    # Shows the list of cached Services.
    ############################################################################################################
    def GET_index(self):
        # Get a list of existing stored VMs in the cache.
        serviceVmRepo = svmrepository.ServiceVMRepository(g.cloudlet)
        vmList = serviceVmRepo.getStoredServiceVMList()

        # Create an item list with the info to display.
        itemList = []
    	for storedVMId in vmList:
            storedVM = vmList[storedVMId]
            newItem = {'service_id':storedVM.metadata.serviceId,
                       'name':storedVM.name,
                       'service_port':storedVM.metadata.servicePort,
                       'folder':storedVM.folder,
                       'action':'Start'}
            itemList.append(newItem)

        # Create and fomat the grid.
    	c.myGrid = Grid(itemList, ['service_id', 'name', 'service_port', 'folder', 'action'])
        c.myGrid.column_formats["action"] = generate_start_button        
        
        # Render the page with the grid.
        return ServicesPage().render()

############################################################################################################
# Helper function to generate a link to start a Service VM for a Service.
############################################################################################################        
def generate_start_button(col_num, i, item):
    startUrl = '/api/servicevm/start?serviceId=' + item["service_id"]
    return HTML.td(HTML.button("Start SVM", onclick="window.location.href='"+ startUrl +"'"))   
