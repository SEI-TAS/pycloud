import logging
import json

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons import g

from webhelpers.html.grid import Grid
from webhelpers.html import HTML

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.manager.lib.pages import ServiceVMsPage
from pycloud.pycloud.pylons.lib import helpers as h

log = logging.getLogger(__name__)

################################################################################################################
# Controller for the ServiceVMs page.
################################################################################################################
class ServiceVMsController(BaseController):

    JSON_OK = json.dumps({"STATUS" : "OK" })
    JSON_NOT_OK = json.dumps({ "STATUS" : "NOT OK"})    

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
        gridItems = []
    	for serviceVMInstanceId in instanceList:
            serviceVMInstance = instanceList[serviceVMInstanceId]
            newItem = {'instance_id':serviceVMInstance.instanceId,
                       'service_id':serviceVMInstance.serviceId,
                       'service_external_port':serviceVMInstance.serviceHostPort,
                       'ssh_port':serviceVMInstance.sshHostPort,                       
                       'folder':serviceVMInstance.getInstanceFolder(),
                       'action':'Stop'}
            gridItems.append(newItem)

        # Create and format the grid.
    	instancesGrid = Grid(gridItems, ['instance_id', 'service_id', 'service_external_port', 'ssh_port', 'folder', 'action'])
        instancesGrid.column_formats["service_id"] = generate_service_id_link
        instancesGrid.column_formats["action"] = generate_action_buttons

        # Pass the grid and render the page.
        svmPage = ServiceVMsPage()
        svmPage.instancesGrid = instancesGrid
        return svmPage.render()
        
    ############################################################################################################
    # Opens a VNC window to a running Service VM Instance.
    ############################################################################################################
    def GET_openvnc(self, id):
        # Get a list of running ServiceVM instances.
        instanceManager = g.cloudlet.instanceManager
        instanceList = instanceManager.getServiceVMInstances()

        if id not in instanceList:
            # If we didn't get a valid id, just return an error message.
            print "Instance id " + id + " was not found on the list of running instances."
            return self.JSON_NOT_OK
            
        # Get the instance associated with this id.
        svmInstance = instanceList[id]
        
        # Try to start the VNC window (this will only work if done on the Cloudlet).
        svmInstance.runningSVM.startVncAndWait(wait=False)
        
        # Everything went well.
        return self.JSON_OK

    ############################################################################################################
    # Starts a new SVM instance of the Service.
    ############################################################################################################        
    def GET_startSVM(self, id):
        # Use the common Instance Manager to start a new instance for the given Service ID.
        instanceManager = g.cloudlet.instanceManager
        instanceManager.getServiceVMInstance(serviceId=id)
        
        # Everything went well.
        return self.JSON_OK        

    ############################################################################################################
    # Stops an existing instance.
    ############################################################################################################        
    def GET_stopSVM(self, id):
        # Use the common Instance Manager to stop an existing instance with the given ID.
        instanceManager = g.cloudlet.instanceManager
        instanceManager.stopServiceVMInstance(instanceId=id)
        
        # Everything went well.
        return self.JSON_OK        
        
############################################################################################################
# Helper function to generate a link for the service id.
############################################################################################################        
def generate_service_id_link(col_num, i, item):
    serviceUrl = h.url_for(controller='services', action='index')
    return HTML.td(HTML.a(item["service_id"], href=serviceUrl))   

############################################################################################################
# Helper function to generate actions for the service vms (stop and vnc buttons).
############################################################################################################        
def generate_action_buttons(col_num, i, item):
    # Button to stop an instance.
    stopUrl = h.url_for(controller='servicevms', action='stopSVM', id=item["instance_id"])
    stopButtonHtml = HTML.button("Stop", onclick=h.literal("stopSVM('"+ stopUrl +"')"), class_="btn btn-primary btn")

    # Button to open VNC window.
    vncUrl = h.url_for(controller='servicevms', action='openvnc', id=item["instance_id"])
    vncButtonHtml = HTML.button("Open VNC", onclick=h.literal("openVNC('"+ vncUrl +"')"), class_="btn btn-primary btn")

    modifyUrl = h.url_for(controller="modify", action='modify', id=item["instance_id"])
    modifyButtonHtml = HTML.button("Modify", onclick=h.literal("openVNC('"+ modifyUrl +"')"), class_="btn btn-primary btn")

    # Render the buttons with the Ajax code to stop the SVM.    
    return HTML.td(stopButtonHtml + " " + vncButtonHtml + " " + modifyButtonHtml)
