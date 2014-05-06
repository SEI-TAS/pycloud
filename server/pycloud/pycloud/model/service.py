__author__ = 'jdroot'

from pycloud.pycloud.mongo import Model
from pycloud.pycloud.model.stored_svm import StoredSVM
from pycloud.pycloud.cloudlet import g_singletonCloudlet as cloudlet


class Service(Model):

    class Meta:
        collection = "services"
        external = ['_id', 'description', 'version', 'tags']
        mapping = {
            'stored_svm': StoredSVM
        }

    @staticmethod
    def by_id(sid=None):
        try:
            service = Service.find_one({'_id': sid})
        except:
            return None
        return service

    def start(self, join=False):
        return cloudlet.instanceManager.start_service_vm(self, joinExisting=join)