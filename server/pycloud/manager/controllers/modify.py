import logging
import os
import json
import urllib

from pylons import request, response, session, tmpl_context as c, url
from pylons import g
from pylons.templating import render_mako as render
from pylons.controllers.util import redirect_to

from webhelpers.html import HTML

from pycloud.pycloud.servicevm import svmrepository
from pycloud.pycloud.servicevm import svmmanager
from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.pycloud.pylons.lib import helpers as h
from pycloud.pycloud.model import Service, ServiceVM, VMImage

from pycloud.manager.lib.pages import ModifyPage

log = logging.getLogger(__name__)

################################################################################################################
# Controller for the Modify page.
################################################################################################################
class ModifyController(BaseController):

    JSON_OK = json.dumps({"STATUS" : "OK" })
    JSON_NOT_OK = json.dumps({ "STATUS" : "NOT OK"})

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
        else:
            # We are editing an existing service.
            page.newService = False
            page.serviceID = serviceID.strip()
            
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
            
                # VM Image values.
                #if(service.vm_image.disk_image != ''):
                #    page.form_values['vmStoredFolder'] = os.path.dirname(service.vm_image.disk_image)
                #page.form_values['vmDiskImageFile'] = service.vm_image.disk_image
                #page.form_values['vmStateImageFile'] = service.vm_image.state_image

        return page

    ################################################################################################################ 
    # Modifying a Service record.
    ################################################################################################################         
    def POST_index(self):
        # Mark the active tab.
        c.services_active = 'active'
        
        # Look for the service with this id.
        serviceId = request.params.get("serviceID").strip()
        service = Service.by_id(serviceId)
        if not service:
            service = Service()
        
        # Service
        service.version     = request.params.get("serviceVersion")
        service.description = request.params.get("serviceDescription")
        service.tags        = request.params.get("serviceTags")
        service.port        = request.params.get("servicePort")
        service.num_users   = request.params.get("numClientsSupported")

        # Requirements
        service.min_memory   = request.params.get("reqMinMem")
        service.ideal_memory = request.params.get("reqIdealMem")

        # App
        appName             = request.params.get("appName")
        appDescription      = request.params.get("appDescription")
        appVersion          = request.params.get("appVersion")
        appPackage          = request.params.get("appPackage")
        appFilename         = request.params.get("appFilename")

        # VM Image info.
        service.vm_image = VMImage()
        service.vm_image.disk_image = request.params.get("vmDiskImageFile")
        service.vm_image.state_image = request.params.get("vmStateImageFile")
        
        # Create or update the information.
        service.save()
        
        # Load the current Stored SVM info.
        # Note that we have to use the original service id to find the data, 
        # since it may have been changed by the user.
        #originalServiceID = request.params.get("originalServiceID", '')

        # Check if we have an originalServiceID value; if not, it means this is a new service.        
        #if(originalServiceID != ''):
            # We have an original id; load the data from the cache.
        #   storedServiceVM = serviceVmRepo.findServiceVM(originalServiceID)
        #else:
        #    storedServiceVM = serviceVmRepo.findServiceVM(serviceID)
        
        # If the service ID changed, rename the folders (as it needs to have the correct id).
        #if(originalServiceID != '' and originalServiceID != serviceID):
        #    serviceVmRepo.renameStoredVM(originalServiceID, serviceID)
        
        # Render the page.
        return redirect_to(controller='services')

    ############################################################################################################
    # Creates a new Service VM and opents it in a VNC window for editing.
    # NOTE: The VNC window will only open on the computer running the server.
    ############################################################################################################
    def POST_createSVM(self):
        # Get the manager.
        print 'Creating SVM...'
        svmManager = svmmanager.ServiceVMManager(g.cloudlet)
        
        # Parse the body of the request as JSON into a python object.
        # First remove URL quotes added to string, and then remove trailing "=" (no idea why it is there).
        parsedJsonString = urllib.unquote(request.body)[:-1]
        fields = json.loads(parsedJsonString)        
        
        # Create an SVM and open a VNC window to modify the VM.
        try:
            newStoredServiceVM = svmManager.createServiceVM(osType = fields['type'], 
                                                            sourceImage = fields['source'],
                                                            serviceId = fields['serviceId'], 
                                                            name = fields['serviceId'],
                                                            port = fields['port'])
            
            #newStoredServiceVM.folder='/home/adminuser/cloudlet/pycloud/data/svmcache/test1'
            #newStoredServiceVM.diskImageFilePath='/home/adminuser/cloudlet/pycloud/data/svmcache/test1/test1.qcow2'
            #newStoredServiceVM.vmStateImageFilepath='/home/adminuser/cloudlet/pycloud/data/svmcache/test1/test1.qcow2.lqs'
        except Exception as e:
            # If there was a problem creating the SVM, return that there was an error.
            print 'Error creating Service VM: ' + str(e);
            return self.JSON_NOT_OK            
        
        # Return information about the created Stored SVM.
        jsonDataStructure = { "FOLDER" : newStoredServiceVM.folder, \
                              "DISK_IMAGE" : newStoredServiceVM.diskImageFilePath, \
                              "STATE_IMAGE" : newStoredServiceVM.vmStateImageFilepath  
                            }      
        jsonDataString = json.dumps(jsonDataStructure)        
        
        # Everything went well.
        print 'Returning newly created SVM data.' + jsonDataString
        return jsonDataString

    ############################################################################################################
    # Opens the Service VM in a VNC window for editing.
    # NOTE: The VNC window will only open on the computer running the server.
    ############################################################################################################
    def GET_openSVM(self, id):
        # Get the manager.
        svmManager = svmmanager.ServiceVMManager(g.cloudlet)
        
        # Open a VNC window to modify the VM.
        try:
            success = svmManager.modifyServiceVM(id)
            
            if(not success):
                # If there was a problem opening the SVM, return that there was an error.
                print 'Error opening Service VM. '
                return self.JSON_NOT_OK                      
        except Exception as e:
            # If there was a problem opening the SVM, return that there was an error.
            print 'Error opening Service VM: ' + str(e);
            return self.JSON_NOT_OK                  
        
        # Everything went well.
        return self.JSON_OK    
 