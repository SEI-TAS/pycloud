__author__ = 'jdroot'

from pycloud.pycloud.mongo import Model
from pycloud.pycloud.model.vmimage import VMImage
from pycloud.pycloud.model.servicevm import ServiceVM
import os
from pylons import g

################################################################################################################
# Represents a Service in the system.
################################################################################################################
class Service(Model):
    # Meta class is needed so that minimongo can map this class onto the database.
    class Meta:
        collection = "services"
        external = ['_id', 'description', 'version', 'tags']
        mapping = {
            'vm_image': VMImage
        }

    ################################################################################################################
    # Constructor.
    ################################################################################################################
    def __init__(self, *args, **kwargs):
        self._id = None
        self.vm_image = None
        self.description = None
        self.version = None
        self.tags = None
        self.port = None
        self.num_users = None
        self.ideal_memory = None
        self.min_memory = None
        super(Service, self).__init__(*args, **kwargs)

    ################################################################################################################
    # Locate a service by its ID
    ################################################################################################################
    # noinspection PyBroadException
    @staticmethod
    def by_id(sid=None):
        try:
            service = Service.find_one({'_id': sid})
        except:
            return None
        return service

    ################################################################################################################
    # Cleanly and safely gets a Service and removes it from the database
    ################################################################################################################
    @staticmethod
    def find_and_remove(sid):
        # Find the right service and remove it. find_and_modify will only return the document with matching id
        return Service.find_and_modify(query={'_id': sid}, remove=True)

    ################################################################################################################
    # Returns a new or existing Service VM instance associated to this service.
    ################################################################################################################
    def get_vm_instance(self, join=False):
        if join:
            svms = ServiceVM.by_service(self._id)
            for svm in svms:
                return svm  # Return the first ServiceVM we found

        # If no ServiceVMs for that ID were found, or join=False, create a new one.
        svm = ServiceVM()
        svm.generate_random_id()
        svm.service_id = self._id
        svm.service_port = self.port
        svm.vm_image = self.vm_image.clone(os.path.join(g.cloudlet.svmInstancesFolder, svm['_id']))
        return svm
    
    ################################################################################################################
    # Returns a VM linked to the original VM image so that it can be modified.
    ################################################################################################################
    def get_root_vm(self):
        svm = ServiceVM()
        svm.generate_random_id()
        svm.service_id = self._id
        svm.service_port = self.port
        svm.vm_image = self.vm_image
        return svm    

    ################################################################################################################
    # Removes this Service and all of its files
    ################################################################################################################
    def destroy(self):
        # Make sure we are no longer in the database
        Service.find_and_remove(self._id)
        
        # Delete our backing files
        self.vm_image.cleanup()
