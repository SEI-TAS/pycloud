__author__ = 'jdroot'

from pycloud.pycloud.mongo import Model
from pycloud.pycloud.model.vmimage import VMImage


class Service(Model):

    class Meta:
        collection = "services"
        external = ['_id', 'description', 'version', 'tags']
        mapping = {
            'vm_image': VMImage
        }

    def __init__(self, *args, **kwargs):
        self._id = None
        self.vm_image = None
        self.description = None
        self.version = None
        self.tags = None
        self.port = None
        self.num_users = None
        self.ideal_memory = None
        super(Service, self).__init__(*args, **kwargs)

    @staticmethod
    def by_id(sid=None):
        try:
            service = Service.find_one({'_id': sid})
        except:
            return None
        return service

    def get_vm_instance(self, join=False):
        pass
        # return cloudlet.instanceManager.start_service_vm(self, joinExisting=join)

    # def get_service_vm(self, join=False):
    #     if join:
    #         svms = ServiceVM.by_service(self._id)
    #         for svm in svms:
    #             return svm
    #     svm = ServiceVM()
    #     svm.service_id = self._id
    #     svm.vm_image = self.vm_image.clone()
    #     svm.start()
    #     svm.save()
    #     return svm