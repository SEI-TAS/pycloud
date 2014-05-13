import logging
import json

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

        # Create an item list with the info to display.
        grid_items = []
        for service in services:
            new_item = {'service_id': service['_id'],
                       'name': service.description,
                       'service_internal_port': service.port,
                       'stored_service_vm_folder': service.vm_image.disk_image,
                       'service_vm_instances': 'SVM',
                       'actions': 'Action'}
            grid_items.append(new_item)

        # Create and fomat the grid.
        servicesGrid = Grid(grid_items, ['service_id', 'name', 'service_internal_port', 'stored_service_vm_folder', 'service_vm_instances', 'actions'])
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
        try:
            service = Service.find_and_remove(id)
            if service:
                service.destroy()
        except Exception as e:
            # If there was a problem removing the service, return that there was an error.
            print 'Error removing Service: ' + str(e)
            return self.JSON_NOT_OK
        
        # Everything went well.
        return self.JSON_OK        

############################################################################################################
# Helper function to generate buttons to see the list of SVMs and to start a new instace.
############################################################################################################        
def generateSVMButtons(col_num, i, item):    
    # Link to the list of Service VM Instances.
    svmListURL = h.url_for(controller='instances')

    # URL to start a new SVM instance.
    startInstanceUrl = h.url_for(controller='instances', action='startInstance', sid=item["service_id"])
    
    # Create a button to the list of service VM Instances, and another to start a new instance.
    linkToSVMButton = HTML.button("View Instances", onclick=h.literal("window.location.href = '" + svmListURL + "';"), class_="btn btn-primary btn")
    newSVMButton = HTML.button("New Instance", onclick=h.literal("startSVM('"+ startInstanceUrl +"', '"+ svmListURL +"')"), class_="btn btn-primary btn")

    # Render the buttons.
    return HTML.td(linkToSVMButton + literal("&nbsp;") + newSVMButton)
    
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
    return HTML.td(editButton + literal("&nbsp;") + removeButton  )       
