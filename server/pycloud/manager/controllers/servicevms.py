import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons import g

from webhelpers.html.grid import Grid
from webhelpers.html import HTML

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.pycloud.servicevm import svmrepository
from pycloud.manager.lib.pages import ServiceVMsPage
from pycloud.pycloud.pylons.lib import helpers as h

log = logging.getLogger(__name__)

################################################################################################################
# Controller for the ServiceVMs page.
################################################################################################################
class ServiceVMsController(BaseController):

    ############################################################################################################
    # Shows the list of running Service VMs.
    ############################################################################################################
    def GET_index(self):
        # Mark the active tab.
        c.servicevms_active = 'active'
        
        # Get a list of running ServiceVM instances.
        instanceManager = g.cloudlet.instanceManager
        instanceList = instanceManager.getServiceVMInstances()

        # Create an item list with the info to display.
        itemList = []
    	for serviceVMInstanceId in instanceList:
            serviceVMInstance = instanceList[serviceVMInstanceId]
            newItem = {'instance_id':serviceVMInstance.instanceId,
                       'service_id':serviceVMInstance.serviceId,
                       'service_port':serviceVMInstance.serviceHostPort,
                       'ssh_port':serviceVMInstance.sshHostPort,                       
                       'folder':serviceVMInstance.getInstanceFolder(),
                       'action':'Stop'}
            itemList.append(newItem)

        # Create and format the grid.
    	c.myGrid = Grid(itemList, ['instance_id', 'service_id', 'service_port', 'ssh_port', 'folder', 'action'])
        c.myGrid.column_formats["service_id"] = generate_service_id_link
        c.myGrid.column_formats["action"] = generate_stop_button

        # Render the page.
        return ServiceVMsPage().render()
        
############################################################################################################
# Helper function to generate a link for the service id.
############################################################################################################        
def generate_service_id_link(col_num, i, item):
    serviceUrl = h.url_for(controller='services', action='index')
    return HTML.td(HTML.a(item["service_id"], href=serviceUrl))   

############################################################################################################
# Helper function to generate a link for the service id.
############################################################################################################        
def generate_stop_button(col_num, i, item):
    stopUrl = '/api/servicevm/stop?instanceId=' + item["instance_id"]
    return HTML.td(HTML.button("Stop", onclick="window.location.href='"+ stopUrl +"'"))   
