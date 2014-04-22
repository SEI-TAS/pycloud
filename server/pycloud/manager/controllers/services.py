import logging
import json

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
    # Shows the list of cached Services.
    ############################################################################################################        
    def GET_removeService(self, id):
        # Remove the stored service VM from the repository.
        serviceVmRepo = svmrepository.ServiceVMRepository(g.cloudlet)
        serviceVmRepo.deleteStoredVM(id)  
        
        # Everything went well.
        return self.JSON_OK        

############################################################################################################
# Helper function to generate buttons to see the list of SVMs and to start a new instace.
############################################################################################################        
def generateSVMButtons(col_num, i, item):    
    # Link to the list of Service VM Instances.
    svmListURL = h.url_for(controller='instances')

    # URL to start a new SVM instance.
    startInstanceUrl = h.url_for(controller='instances', action='startInstance', id=item["service_id"])
    
    # Create a button to the list of service VM Instances, and another to start a new instance.
    linkToSVMButton = HTML.button("View Instances", onclick=h.literal("window.location.href = '" + svmListURL + "';"), class_="btn btn-primary btn")
    newSVMButton = HTML.button("New Instance", onclick=h.literal("startSVM('"+ startInstanceUrl +"', '"+ svmListURL +"')"), class_="btn btn-primary btn")

    # Render the buttons.
    return HTML.td(linkToSVMButton + " " + newSVMButton)
    
############################################################################################################
# Helper function to generate buttons to edit or delete services.
############################################################################################################        
def generateActionButtons(col_num, i, item):
    # Link and button to edit the service.
    editServiceURL = h.url_for(controller='modify', action='index', id=item["service_id"])
    editButton = HTML.button("Edit Service", onclick=h.literal("window.location.href = '" + editServiceURL + "';"), class_="btn btn-primary btn")
    
    # Ajax URL to remove the service.
    removeServiceURL = h.url_for(controller='services', action='removeService', id=item["service_id"])
    removeButton = HTML.button("Remove Service", onclick="removeServiceConfirmation('" + removeServiceURL + "', '" + item["service_id"] + "');", class_="btn btn-primary btn")
    
    # Render the buttons.
    return HTML.td(editButton + " " + removeButton  )       
