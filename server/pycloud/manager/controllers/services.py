import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons import g

from webhelpers.html.grid import Grid
from webhelpers.html import HTML

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.pycloud.servicevm import svmrepository
from pycloud.manager.lib.pages import ServicesPage
from pycloud.pycloud.pylons.lib import helpers as h

log = logging.getLogger(__name__)

################################################################################################################
# Controller for the Services page.
################################################################################################################
class ServicesController(BaseController):

    ############################################################################################################
    # Shows the list of cached Services.
    ############################################################################################################
    def GET_index(self):
        # Mark the active tab.
        c.services_active = 'active'
    
        # Get a list of existing stored VMs in the cache.
        serviceVmRepo = svmrepository.ServiceVMRepository(g.cloudlet)
        vmList = serviceVmRepo.getStoredServiceVMList()

        # Create an item list with the info to display.
        gridItems = []
    	for storedVMId in vmList:
            storedVM = vmList[storedVMId]
            newItem = {'service_id':storedVM.metadata.serviceId,
                       'name':storedVM.name,
                       'service_internal_port':storedVM.metadata.servicePort,
                       'stored_service_vm_folder':storedVM.folder,
                       'service_vm_instances':'Start'}
            gridItems.append(newItem)

        # Create and fomat the grid.
    	servicesGrid = Grid(gridItems, ['service_id', 'name', 'service_internal_port', 'stored_service_vm_folder', 'service_vm_instances'])
        servicesGrid.column_formats["service_vm_instances"] = generate_start_button        
        
        # Pass the grid and render the page.
        servicesPage = ServicesPage()
        servicesPage.servicesGrid = servicesGrid
        return servicesPage.render()

############################################################################################################
# Helper function to generate a button to start a Service VM for a Service through Ajax.
############################################################################################################        
def generate_start_button(col_num, i, item):
    # TODO: we will need a centralized way of getting API URLs.
    startUrl = '/api/servicevm/start?serviceId=' + item["service_id"]
    
    # After starting the SVM, we will redirect to the Service VM list page.
    redirectUrl = h.url_for(controller='servicevms')
    
    # Render the button with the Ajax code to start the SVM.
    linkToSVMButton = HTML.button("View Instances", onclick=h.literal("window.location.href = '" + redirectUrl + "';"), class_="btn btn-primary btn")
    newSVMButton = HTML.button("New Instance", onclick=h.literal("startSVM('"+ startUrl +"', '"+ redirectUrl +"')"), class_="btn btn-primary btn")
    return HTML.td(linkToSVMButton + " " + newSVMButton)   
