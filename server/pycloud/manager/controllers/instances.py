import logging
import json
import time

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons import g

from webhelpers.html.grid import Grid
from webhelpers.html import HTML

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.manager.lib.pages import InstancesPage
from pycloud.pycloud.pylons.lib import helpers as h

log = logging.getLogger(__name__)

################################################################################################################
# Controller for the ServiceVMs Instances page.
################################################################################################################
class InstancesController(BaseController):

    JSON_OK = json.dumps({"STATUS" : "OK" })
    JSON_NOT_OK = json.dumps({ "STATUS" : "NOT OK"})
    
    ############################################################################################################
    # Shows the list of running Service VM instances.
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
        instancesPage = InstancesPage()
        instancesPage.instancesGrid = instancesGrid
        return instancesPage.render()
        
    ############################################################################################################
    # Opens a VNC window to a running Service VM Instance.
    ############################################################################################################
    def GET_openVNC(self, id):
        # Get a list of running ServiceVM instances.
        instanceManager = g.cloudlet.instanceManager
        instanceList = instanceManager.getServiceVMInstances()

        if id not in instanceList:
            # If we didn't get a valid id, just return an error message.
            print "Instance id " + id + " was not found on the list of running instances."
            return self.JSON_NOT_OK
            
        # Get the instance associated with this id.
        svmInstance = instanceList[id]
        
        try:
            # Try to start the VNC window (this will only work if done on the Cloudlet).
            svmInstance.serviceVM.startVncAndWait(wait=False)
        except Exception as e:        
            # If there was a problem connecting through VNC, return that there was an error.
            print 'Error opening VNC window: ' + str(e);
            return self.JSON_NOT_OK     
        
        # Everything went well.
        return self.JSON_OK

    ############################################################################################################
    # Starts a new SVM instance of the Service.
    ############################################################################################################        
    def GET_startInstance(self, id):
        try:
            # Use the common Instance Manager to start a new instance for the given Service ID.        
            instanceManager = g.cloudlet.instanceManager
            instanceManager.getServiceVMInstance(serviceId=id)
        except Exception as e:
            # If there was a problem starting the instance, return that there was an error.
            print 'Error starting Service VM Instance: ' + str(e);
            return self.JSON_NOT_OK     
        
        # Everything went well.
        return self.JSON_OK        

    ############################################################################################################
    # Stops an existing instance.
    ############################################################################################################        
    def GET_stopInstance(self, id):
        try:    
            # Use the common Instance Manager to stop an existing instance with the given ID.
            instanceManager = g.cloudlet.instanceManager
            instanceManager.stopServiceVMInstance(instanceId=id)
        except Exception as e:
            # If there was a problem stopping the instance, return that there was an error.
            print 'Error stopping Service VM Instance: ' + str(e);
            return self.JSON_NOT_OK               
        
        # Everything went well.
        return self.JSON_OK
    
    ############################################################################################################
    # Checks if there are changes in the instance list, and returns a changestamp of the change.
    ############################################################################################################        
    def GET_getLastChangestamp(self):
        try:    
            # Get the list of running instances.
            instanceManager = g.cloudlet.instanceManager
            instanceList = instanceManager.getServiceVMInstances()
            
            # Turn into a string for an easy comparison, and compare it to the last stored one.
            separator = ','
            currentInstancesIdList = separator.join(str(id) for id in instanceList)
            if(instanceManager.instancesIdList != currentInstancesIdList):
                # Update the list string, and update the timestamp.
                instanceManager.instancesIdList = currentInstancesIdList
                instanceManager.lastChangestamp = time.time()
        except Exception as e:
            # If there was a problem stopping the instance, return that there was an error.
            print 'Error getting list of instance changes: ' + str(e);
            return self.JSON_NOT_OK               
        
        # Return the timestamp.
        jsonTimestamp = json.dumps({"LAST_CHANGE_STAMP" : str(instanceManager.lastChangestamp) })
        return jsonTimestamp
        
############################################################################################################
# Helper function to generate a link for the service id to the service details.
############################################################################################################        
def generate_service_id_link(col_num, i, item):
    editServiceURL = h.url_for(controller='modify', action='index', id=item["service_id"])
    
    return HTML.td(HTML.a(item["service_id"], href=editServiceURL))   

############################################################################################################
# Helper function to generate actions for the service vms (stop and vnc buttons).
############################################################################################################        
def generate_action_buttons(col_num, i, item):
    # Button to stop an instance.
    stopUrl = h.url_for(controller='instances', action='stopInstance', id=item["instance_id"])
    stopButtonHtml = HTML.button("Stop", onclick=h.literal("stopSVM('"+ stopUrl +"')"), class_="btn btn-primary btn")

    # Button to open VNC window.
    vncUrl = h.url_for(controller='instances', action='openVNC', id=item["instance_id"])
    vncButtonHtml = HTML.button("Open VNC", onclick=h.literal("openVNC('"+ vncUrl +"')"), class_="btn btn-primary btn")

    # Render the buttons with the Ajax code to stop the SVM.    
    return HTML.td(stopButtonHtml + " " + vncButtonHtml)
