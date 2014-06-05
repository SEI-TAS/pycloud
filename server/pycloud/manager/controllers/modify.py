import logging
import os
import json
import urllib

from pylons import request, response, session, tmpl_context as c, url
from pylons import g
from pylons.templating import render_mako as render
from pylons.controllers.util import redirect_to

from webhelpers.html import HTML

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.pycloud.pylons.lib import helpers as h
from pycloud.pycloud.model import Service, ServiceVM, VMImage
from pycloud.pycloud.pylons.lib.util import asjson
from pycloud.pycloud.pylons.lib.util import dumps

from pycloud.manager.lib.pages import ModifyPage

log = logging.getLogger(__name__)

################################################################################################################
# Controller for the Modify page.
################################################################################################################
class ModifyController(BaseController):

    JSON_OK = {"STATUS" : "OK" }
    JSON_NOT_OK = { "STATUS" : "NOT OK"}

    ################################################################################################################ 
    # Called when laading the page to add or edit a service.
    ################################################################################################################ 
    def GET_index(self, id=None):
        # Mark the active tab.
        c.services_active = 'active'
                
        # Load the data into the page.
        page = ModifyPage()
        
        # If we are loading data from an existing Service, load it.
        serviceID = id
        page = self.loadDataIntoPage(page, serviceID)

        # Render the page with the data.
        return page.render()
    
    ################################################################################################################ 
    # Loads data about the stored service vm into a page, and returns the filled page.
    ################################################################################################################         
    def loadDataIntoPage(self, page, serviceID):                  
        # Setup the page to render.
        page.form_values = {}
        page.form_errors = {}
        
        # URL to create a new Service VM.
        page.createSVMURL =  h.url_for(controller="modify", action='createSVM')
        
        # URL to open an SVM.
        page.openSVMURL = h.url_for(controller="modify", action='openSVM')
        
        # URL to create an App.
        page.createAppURL = h.url_for(controller="modify", action='openSVM')
                
        # Check if we are editing or creating a new service.
        creatingNew = serviceID is None
        if(creatingNew):
            # We are creating a new service.
            page.newService = True
            page.serviceID = ''
            page.serviceIDChangeDisabled = False
        else:
            # We are editing an existing service.
            page.newService = False
            page.serviceID = serviceID.strip()
            page.serviceIDChangeDisabled = True
            
            # Look for the service with this id.
            service = Service.by_id(serviceID)
            
            # Set the data fields.
            page.form_values['serviceID'] = serviceID
            if service:
                # Metadata values.
                page.form_values['servicePort'] = service.port
                page.form_values['serviceDescription'] = service.description
                page.form_values['serviceVersion'] = service.version
                page.form_values['serviceTags'] = service.tags
                page.form_values['numClientsSupported'] = service.num_users
                page.form_values['reqMinMem'] = service.min_memory
                page.form_values['reqIdealMem'] = service.ideal_memory
            
                # VM Image values. The ...Value fields are for storing data, while the others are for
                # showing it only. Since the vmDiskImageFile and vmStateImageFile fields are disabled,
                # (read-only) their value is not sent, and we have to store that value in hidden variables.
                if(service.vm_image.disk_image):
                    page.form_values['vmStoredFolder'] = os.path.dirname(service.vm_image.disk_image)
                    page.form_values['vmDiskImageFile'] = service.vm_image.disk_image
                    page.form_values['vmDiskImageFileValue'] = service.vm_image.disk_image
                if(service.vm_image.state_image):
                    page.form_values['vmStateImageFile'] = service.vm_image.state_image
                    page.form_values['vmStateImageFileValue'] = service.vm_image.state_image

        return page

    ################################################################################################################ 
    # Modifying a Service record.
    ################################################################################################################         
    def POST_index(self):
        # Mark the active tab.
        c.services_active = 'active'
        
        # Look for the service with this id.
        serviceId = request.params.get("serviceID")
        if not serviceId:
            serviceId = request.params.get("originalServiceID")
        serviceId = serviceId.strip()
        print 'Creating new service with id ' + serviceId
        service = Service.by_id(serviceId)
        if not service:
            service = Service()
        
        # Service
        service._id         = serviceId
        service.version     = request.params.get("serviceVersion")
        service.description = request.params.get("serviceDescription")
        service.tags        = request.params.get("serviceTags")
        service.port        = request.params.get("servicePort")
        service.num_users   = request.params.get("numClientsSupported")

        # Requirements
        service.min_memory   = request.params.get("reqMinMem")
        service.ideal_memory = request.params.get("reqIdealMem")

        # VM Image info.
        service.vm_image = VMImage()
        service.vm_image.disk_image = request.params.get("vmDiskImageFileValue")
        service.vm_image.state_image = request.params.get("vmStateImageFileValue")
        
        # Create or update the information.
        service.save()
               
        # Render the page.
        return redirect_to(controller='services')

    ############################################################################################################
    # Creates a new Service VM and opents it in a VNC window for editing.
    # NOTE: The VNC window will only open on the computer running the server.
    ############################################################################################################
    @asjson
    def POST_createSVM(self):
        # Get the manager.
        print 'Creating SVM...'
        svm = ServiceVM()
        svm.generate_random_id()
        
        # Parse the body of the request as JSON into a python object.
        # First remove URL quotes added to string, and then remove trailing "=" (no idea why it is there).
        parsedJsonString = urllib.unquote(request.body)[:-1]
        fields = json.loads(parsedJsonString)        
        
        # Create an SVM and open a VNC window to modify the VM.
        svm.service_id = fields['serviceId']
        try:
            print 'newVmFolder: ', g.cloudlet.newVmFolder
            print 'svm._id: ', svm._id
            # Set up a new VM image.
            temp_svm_folder = os.path.join(g.cloudlet.newVmFolder, svm._id)
            print 'temp_svm_folder: ', temp_svm_folder
            new_disk_image = os.path.join(temp_svm_folder, svm.service_id)
            new_vm_image = VMImage()
            print 'calling VMImage#create with "%s" and "%s"' % (fields['source'], new_disk_image)
            new_vm_image.create(fields['source'], new_disk_image)
                        
            # Get the XML descriptor from the config.
            osType = fields['type']
            if(osType == 'Windows'):
                template_xml_file = os.path.abspath(g.cloudlet.newVmWinXml)
            else:
                template_xml_file = os.path.abspath(g.cloudlet.newVmLinXml)

            # Create the VM (this will also start it).
            print "Creating and starting VM for user access..."
            svm.vm_image = new_vm_image
            svm.service_port = fields['port']
            #svm.addForwardedSshPort()            
            svm.create(template_xml_file)
            
            # Open a synchronous VNC window to it.
            print "Loading VM for user access..."
            svm.open_vnc(wait=True)
            
            # Save the VM state.
            print "VNC GUI closed, saving machine state..."
            svm.stop()
            print "Service VM stopped, and machine state saved."
            
            # Permanently store the VM.
            print 'Moving Service VM Image to cache.'
            svm.vm_image.move(os.path.join(g.cloudlet.svmCache, svm.service_id))
        except Exception as e:
            # If there was a problem creating the SVM, return that there was an error.
            print 'Error creating Service VM: ' + str(e);
            if new_vm_image:
                new_vm_image.cleanup(force=True)
            return self.JSON_NOT_OK            
        
        # Everything went well.
        print 'Returning newly created VM data.'
        return svm.vm_image

    ############################################################################################################
    # Opens the Service VM in a VNC window for editing.
    # NOTE: The VNC window will only open on the computer running the server.
    ############################################################################################################
    def GET_openSVM(self, id):        
        # Open a VNC window to modify the VM.
        try:
            # Get the service info.
            service = Service.by_id(id)
            
            # Get the service vm, and enable modification to its files.
            svm = service.get_root_vm()
            svm.vm_image.unprotect()

            # Start the VM for interactive modification.
            print "Starting VM for user access..."
            # svm.addForwardedSshPort()
            svm.start()

            # Open a synchronous VNC window to it.
            print "Loading VM for user access..."
            svm.open_vnc(wait=True)
            
            # Save the VM state.
            print "VNC GUI closed, saving machine state..."
            svm.stop()
            print "Service VM stopped, and machine state saved."
            
            # Destroy the service VM.
            svm.destroy()     
            
            # Make the VM image read only again.
            svm.vm_image.protect()
        except Exception as e:
            # If there was a problem opening the SVM, return that there was an error.
            print 'Error opening Service VM: ' + str(e);
            return dumps(self.JSON_NOT_OK)                  
        
        # Everything went well.
        return dumps(self.JSON_OK)    
 