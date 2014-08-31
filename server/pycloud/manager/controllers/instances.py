import logging
import json
import time
import os.path

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons import g

from webhelpers.html.grid import Grid
from webhelpers.html import HTML
from webhelpers.html import literal

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.manager.lib.pages import InstancesPage
from pycloud.pycloud.pylons.lib import helpers as h
from pycloud.pycloud.model import Service, ServiceVM
from pycloud.pycloud.pylons.lib.util import asjson
from pycloud.pycloud.pylons.lib.util import dumps

log = logging.getLogger(__name__)

################################################################################################################
# Controller for the ServiceVMs Instances page.
################################################################################################################
class InstancesController(BaseController):

    JSON_OK = {"STATUS" : "OK" }
    JSON_NOT_OK = { "STATUS" : "NOT OK"}
    
    ############################################################################################################
    # Shows the list of running Service VM instances.
    # TODO: Update to use new model
    ############################################################################################################
    def GET_index(self):
        # Mark the active tab.
        c.servicevms_active = 'active'

        svms = ServiceVM.find()

        grid_items = []
        for svm in svms:
            grid_items.append(
                {
                    'instance_id': svm['_id'],
                    'service_id': svm.service_id,
                    'service_external_port': svm.port,
                    'ssh_port': svm.ssh_port,
                    'vnc_port': svm.vnc_port,
                    #'folder': os.path.dirname(svm.vm_image.disk_image),
                    'action': 'Stop'
                }
            )

        # Create and format the grid.
        instancesGrid = Grid(grid_items, ['instance_id', 'service_id', 'service_external_port', 'ssh_port', 'vnc_port', 'action'])
        instancesGrid.column_formats["service_id"] = generate_service_id_link
        instancesGrid.column_formats["action"] = generate_action_buttons

        # Pass the grid and render the page.
        instancesPage = InstancesPage()
        instancesPage.instancesGrid = instancesGrid
        return instancesPage.render()
        
    ############################################################################################################
    # Opens a VNC window to a running Service VM Instance.
    # TODO: Update to use new model
    ############################################################################################################
    def GET_openVNC(self, id):
        try:            
            # Get the instance associated with this id.
            svm = ServiceVM.by_id(id)
            
            if not svm:
                # If we didn't get a valid id, just return an error message.
                print "Service VM id " + id + " was not found on the list of running instances."
                return dumps(self.JSON_NOT_OK)       
            
            # Try to start the VNC window (this will only work if done on the Cloudlet).
            svm.open_vnc(wait=False)
        except Exception as e:        
            # If there was a problem connecting through VNC, return that there was an error.
            print 'Error opening VNC window: ' + str(e);
            return dumps(self.JSON_NOT_OK)  
        
        # Everything went well.
        return dumps(self.JSON_OK)

    ############################################################################################################
    # Starts a new SVM instance of the Service.
    ############################################################################################################  
    def GET_startInstance(self, sid):
        # Look for the service with this id
        service = Service.by_id(sid)
        if service:
            clone_full_image = True
            print request.params.get('clone_full_image')
            if request.params.get('clone_full_image'):
                clone_full_image = False
            # Get a ServiceVM instance
            svm = service.get_vm_instance(clone_full_image=clone_full_image)
            try:
                # Start the instance, if it works, save it and return ok
                svm.start()
                svm.save()
                return dumps({"STATUS": "OK", "SVM_ID": svm._id, "VNC_PORT": svm.vnc_port})
            except Exception as e:
                # If there was a problem starting the instance, return that there was an error.
                print 'Error starting Service VM Instance: ' + str(e)
                return dumps(self.JSON_NOT_OK)

        return dumps(self.JSON_NOT_OK)

    ############################################################################################################
    # Stops an existing instance.
    ############################################################################################################
    def GET_stopInstance(self, id):
        try:    
            # Stop an existing instance with the given ID.
            svm = ServiceVM.find_and_remove(id)
            svm.destroy()
        except Exception as e:
            # If there was a problem stopping the instance, return that there was an error.
            print 'Error stopping Service VM Instance: ' + str(e)
            return dumps(self.JSON_NOT_OK)               
        
        # Everything went well.
        return dumps(self.JSON_OK)
    
    ############################################################################################################
    # Checks if there are changes in the instance list, and returns a changestamp of the change.
    ############################################################################################################    
    @asjson    
    def GET_getLastChangestamp(self):
        try:    
            # Get the list of running instances.
            svm_list = ServiceVM.find()
            return 
            
            # Turn into a string for an easy comparison, and compare it to the last stored one.
            separator = ','
            #currentInstancesIdList = separator.join(str(id) for id in svm_list)
            #if(instanceManager.instancesIdList != currentInstancesIdList):
                # Update the list string, and update the timestamp.
                #instanceManager.instancesIdList = currentInstancesIdList
                #instanceManager.lastChangestamp = time.time()
        except Exception as e:
            # If there was a problem stopping the instance, return that there was an error.
            print 'Error getting list of instance changes: ' + str(e);
            return self.JSON_NOT_OK               
        
        # Return the timestamp.
        #jsonTimestamp = json.dumps({"LAST_CHANGE_STAMP" : str(instanceManager.lastChangestamp) })
        #return jsonTimestamp
        
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
    return HTML.td(stopButtonHtml + literal("&nbsp;") + vncButtonHtml)
