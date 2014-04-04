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
                       'service_vm_instances':'SVM',
                       'actions':'Action'}
            gridItems.append(newItem)

        # Create and fomat the grid.
    	servicesGrid = Grid(gridItems, ['service_id', 'name', 'service_internal_port', 'stored_service_vm_folder', 'service_vm_instances', 'actions'])
        servicesGrid.column_formats["service_vm_instances"] = generateSVMButtons
        servicesGrid.column_formats["actions"] = generateActionButtons
        
        # Pass the grid and render the page.
        servicesPage = ServicesPage()
        servicesPage.servicesGrid = servicesGrid
        return servicesPage.render()

############################################################################################################
# Helper function to generate buttons to see the list of SVMs and to start a new instace.
############################################################################################################        
def generateSVMButtons(col_num, i, item):
    # TODO: we will need a centralized way of getting API URLs.
    startInstanceUrl = '/api/servicevm/start?serviceId=' + item["service_id"]
    
    # After starting the SVM, we will redirect to the Service VM list page.
    svmListURL = h.url_for(controller='servicevms')
    
    # Create a button to the list of service VMs, and another to start a new instance.
    linkToSVMButton = HTML.button("View Instances", onclick=h.literal("window.location.href = '" + svmListURL + "';"), class_="btn btn-primary btn")
    newSVMButton = HTML.button("New Instance", onclick=h.literal("startSVM('"+ startInstanceUrl +"', '"+ svmListURL +"')"), class_="btn btn-primary btn")

    # Render the buttons.
    return HTML.td(linkToSVMButton + " " + newSVMButton)
    
############################################################################################################
# Helper function to generate buttons to edit or delete services.
############################################################################################################        
def generateActionButtons(col_num, i, item):
    # Link to edit the service.
    editServiceURL = h.url_for(controller='modify')

    # Create a button to edit and a button to remove a service.
    editButton = HTML.button("Edit Service", onclick=h.literal("window.location.href = '" + editServiceURL + "&serviceId= " + item["service_id"] + "';"), class_="btn btn-primary btn")
    removeButton = HTML.button("Remove Service", onclick="#", class_="btn btn-primary btn")

    # Render the buttons.
    return HTML.td(editButton + " " + removeButton)
