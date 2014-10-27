__author__ = 'jdroot'

from pycloud.pycloud.mongo import Model, ObjectID
from pycloud.pycloud.model.vmimage import VMImage
from pycloud.pycloud.model.servicevm import ServiceVM
import os
from pylons import g

# ###############################################################################################################
# Represents a Service in the system.
################################################################################################################
class Service(Model):
    # Meta class is needed so that minimongo can map this class onto the database.
    class Meta:
        collection = "services"
        external = ['_id', 'service_id', 'description', 'version', 'tags']
        mapping = {
            'vm_image': VMImage
        }

    ################################################################################################################
    # Constructor.
    ################################################################################################################
    def __init__(self, *args, **kwargs):
        self.service_id = None
        self.vm_image = None
        self.description = None
        self.version = None
        self.tags = []
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
    def by_internal_id(sid=None):
        rid = sid
        if not isinstance(rid, ObjectID):
            # noinspection PyBroadException
            try:
                rid = ObjectID(rid)
            except:
                return None
        return Service.find_one({'_id': rid})   

    ################################################################################################################
    # Locate a service by its ID
    ################################################################################################################
    # noinspection PyBroadException
    @staticmethod
    def by_id(sid=None):
        try:
            service = Service.find_one({'service_id': sid})
        except:
            return None
        return service

    ################################################################################################################
    # Cleanly and safely gets a Service and removes it from the database
    ################################################################################################################
    @staticmethod
    def find_and_remove(sid):
        # Find the right service and remove it. find_and_modify will only return the document with matching id
        return Service.find_and_modify(query={'service_id': sid}, remove=True)

    ################################################################################################################
    # Returns a new or existing Service VM instance associated to this service.
    ################################################################################################################
    def get_vm_instance(self, join=False, clone_full_image=False):
        print "get_vm_instance of ", self.service_id
        print "  self.num_users = ", self.num_users
        print "  join = ", join
        print "Type num users: ", type(self.num_users)
        print "type join: ", type(join)
        print "self.num_users == 0: ", (self.num_users == 0)
        print "join == True: ", (join == True)
        if self.num_users == 0 and join:
            svms = ServiceVM.by_service(self._id)
            for svm in svms:
                return svm  # Return the first ServiceVM we found

        # If no ServiceVMs for that ID were found, or join=False, create a new one.
        svm = ServiceVM()
        svm.generate_random_id()
        svm.service_id = self.service_id
        svm.service_port = self.port
        svm.vm_image = self.vm_image.clone(os.path.join(g.cloudlet.svmInstancesFolder, svm['_id']), clone_full_image=clone_full_image)
        return svm

    ################################################################################################################
    # Returns a VM linked to the original VM image so that it can be modified.
    ################################################################################################################
    def get_root_vm(self):
        svm = ServiceVM()
        svm.generate_random_id()
        svm.service_id = self.service_id
        svm.service_port = self.port
        svm.vm_image = self.vm_image
        return svm

    ################################################################################################################
    # Removes this Service and all of its files
    ################################################################################################################
    def destroy(self):
        # Make sure we are no longer in the database
        Service.find_and_remove(self.service_id)

        # Delete our backing files
        self.vm_image.cleanup()

    ################################################################################################################
    # Removes this Service and all of its files
    ################################################################################################################
    def export(self):
        # We manually turn the service in to a dict because @asjson forces external fields only
        import json
        return json.dumps(
            {
                "service_id": self.service_id,
                "vm_image": self.vm_image.export(),
                "description": self.description,
                "version": self.version,
                "tags": [str(tag) for tag in self.tags],
                "port": self.port,
                "num_users": self.num_users,
                "ideal_memory": self.ideal_memory,
                "min_memory": self.min_memory
            }
        )
