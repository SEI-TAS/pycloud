import logging
import os
import os.path

from pylons import request, response, session, tmpl_context as c, url
from pylons import g
from pylons.controllers.util import redirect_to

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.pycloud.pylons.lib import helpers as h
from pycloud.pycloud.model import Service, ServiceVM, VMImage
from pycloud.pycloud.pylons.lib.util import asjson, encoded_json_to_dict

from pycloud.manager.lib.pages import ModifyPage

from pycloud.pycloud.utils import ajaxutils

log = logging.getLogger(__name__)

################################################################################################################
# Controller for the Modify page.
################################################################################################################
class ModifyController(BaseController):

    ################################################################################################################ 
    # Called when loading the page to add or edit a service.
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
        page.createSVMURL = h.url_for(controller="modify", action='createSVM')

        # Check if we are editing or creating a new service.
        creatingNew = serviceID is None
        page.openVNCUrl = h.url_for(controller='instances', action='openVNC', id=None, action_name=None)
        page.saveInstanceURL = h.url_for(controller='modify', action='saveInstanceToRoot', id=None, action_name=None)
        page.stopInstanceURL = h.url_for(controller='instances', action='stopInstance', id=None, action_name=None)
        page.startInstanceURL = h.url_for(controller='instances', action='startInstance', id=None, action_name=None)
        page.chooseImageURL = h.url_for(controller='modify', action='getImageInfo', id=None, action_name=None)
        if(creatingNew):
            # We are creating a new service.
            page.newService = True
            page.internalServiceId = ''
        else:
            # Look for the service with this id.
            service = Service.by_id(serviceID)
            
            # We are editing an existing service.
            page.newService = False
            page.internalServiceId = service._id

            if service:
                # Metadata values.
                page.form_values['serviceID'] = service.service_id
                page.form_values['servicePort'] = service.port
                page.form_values['serviceDescription'] = service.description
                page.form_values['serviceVersion'] = service.version
                page.form_values['serviceTags'] = ",".join(service.tags)
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

        # Get the internal id.        
        internalServiceId = request.params.get("internalServiceId")
        print 'Internal service id ' + internalServiceId
        
        # Check if there is another service already with this service id.
        service_id = request.params.get("serviceID")
        previous_service = Service.by_id(service_id)

        if previous_service and str(previous_service['_id']) != internalServiceId:
            # TODO: somehow notify the error.
            print "A service can't have the same service id as an existing service."
            return redirect_to(controller='services')
        
        # Look for a service with this id.
        service = Service.by_internal_id(internalServiceId)
        if not internalServiceId or not service:
            # If we didn't get an internal service id or we couldn't find such service, we are creating a new one.
            print 'Creating new service'
            service = Service()
        else:
            print 'Service found, with internal id ' + str(service._id)
        
        # Service
        service.service_id  = request.params.get("serviceID")
        service.version     = request.params.get("serviceVersion")
        service.description = request.params.get("serviceDescription")
        service.tags        = request.params.get("serviceTags")
        if service.tags:
            service.tags = service.tags.split(',')
        else:
            service.tags = []
        service.port        = request.params.get("servicePort")
        service.num_users   = request.params.get("numClientsSupported", "")

        try:
            service.num_users = int(service.num_users)
        except Exception as e:
            service.num_users = 0


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
    # Creates a new Service VM and opens it in a VNC window for editing.
    # NOTE: The VNC window will only open on the computer running the server.
    ############################################################################################################
    @asjson
    def POST_createSVM(self):
        # Get the manager.
        print 'Creating SVM...'
        svm = ServiceVM()
        svm.generate_random_id()
        
        # Parse the body of the request as JSON into a python object.
        fields = encoded_json_to_dict(request.body)
        
        # Create an SVM and open a VNC window to modify the VM.
        svm.service_id = fields['serviceId']
        try:
            # Set up a new VM image.
            print 'newVmFolder: ', g.cloudlet.newVmFolder
            print 'svm._id: ', svm._id
            temp_svm_folder = os.path.join(g.cloudlet.newVmFolder, svm._id)
            print 'temp_svm_folder: ', temp_svm_folder
            new_disk_image = os.path.join(temp_svm_folder, svm.service_id)
            new_vm_image = VMImage()
            print 'calling VMImage#create with "%s" and "%s"' % (fields['source'], new_disk_image)
            new_vm_image.create(fields['source'], new_disk_image)
            new_vm_image.unprotect()

            # Set the OS type.
            os_type = fields['type']
            if os_type == 'Windows':
                svm.os = "win"
            else:
                svm.os = "lin"

            # Create the VM (this will also start it).
            print "Creating and starting VM for user access..."
            template_xml_file = os.path.abspath(g.cloudlet.newVmXml)
            svm.vm_image = new_vm_image
            svm.service_port = fields['port']
            svm.create(template_xml_file)
            svm.save()

            # Return info about the svm.
            svm_info = {'_id': svm._id,
                        'vnc_port': svm.vnc_port}
            return svm_info
        except Exception as e:
            # If there was a problem creating the SVM, return that there was an error.
            msg = 'Error creating Service VM: ' + str(e)
            import traceback, sys
            traceback.print_exc(file=sys.stdout)
            #if svm.vm_image:
            #    svm.vm_image.cleanup(force=True)

            return ajaxutils.show_and_return_error_dict(msg)

    ############################################################################################################
    # Stops and saves a Service VM that was edited to its permanent root VM image.
    ############################################################################################################
    @asjson
    def GET_saveInstanceToRoot(self, id):
        try:
            if id is None:
                msg = "No VM id was provided, VM can't be saved."
                return ajaxutils.show_and_return_error_dict(msg)

            # Save the VM state.
            print "Saving machine state for SVM with id " + str(id)
            svm = ServiceVM.find_and_remove(id)
            svm.stop(foce_save_state=True)
            print "Service VM stopped, and machine state saved."

            print 'Editing? ' + str(request.params.get('editing'))
            if request.params.get('editing') == 'false':
                # Use the service id as the folder for this new saved SVM.
                vm_image_folder = os.path.join(g.cloudlet.svmCache, svm.service_id)
            else:
                # Get the folder of the permanent VM image, to overwrite the previous one.
                service = Service.by_id(svm.service_id)
                vm_image_folder = os.path.dirname(service.vm_image.disk_image)

            # Permanently store the VM.
            print 'Moving Service VM Image to cache, from folder {} to folder {}.'.format(os.path.dirname(svm.vm_image.disk_image), vm_image_folder)
            svm.vm_image.move(vm_image_folder)

            # Make the VM image read only.
            print 'Making VM Image read-only.'
            try:
                svm.vm_image.protect()
                print 'VM Image updated.'
            except:
                print 'Error making VM read-only. Check permissions on file.'

            # Everything went well, return image info.
            return svm.vm_image
        except Exception as e:
            # If there was a problem opening the SVM, return that there was an error.
            msg = 'Error saving Service VM: ' + str(e)
            return ajaxutils.show_and_return_error_dict(msg)

    ############################################################################################################
    # Loads information about the VM image in the given folder.
    ############################################################################################################
    @asjson
    def POST_getImageInfo(self):
        # Parse the body of the request as JSON into a python object.
        fields = encoded_json_to_dict(request.body)

        # Load VM Image information from the folder.
        image_folder = fields['folder']
        vm_image = VMImage()
        try:
            vm_image.load_from_folder(image_folder)
        except Exception as e:
            msg = 'Error selecting existing VM image: ' + str(e)
            return ajaxutils.show_and_return_error_dict(msg)

        return vm_image
