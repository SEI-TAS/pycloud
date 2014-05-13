__author__ = 'jdroot'

from pymongo import Connection
from pymongo.errors import ConnectionFailure
import psutil
import os
import shutil
from pycloud.pycloud.servicevm import instancemanager
from pycloud.pycloud.utils import portmanager
from pycloud.pycloud.vm.vmutils import destroy_all_vms
import pycloud.pycloud.mongo.model as model


# Singleton object to maintain intra- and inter-app variables.
_g_singletonCloudlet = None

################################################################################################################
# Creates the Cloudlet singleton, or gets an instance of it if it had been already created.
################################################################################################################
def get_cloudlet_instance(config=None):
    # Only create it if we don't have a reference already.
    global _g_singletonCloudlet
    if not _g_singletonCloudlet:
        print 'Creating Cloudlet singleton.'
        _g_singletonCloudlet = Cloudlet(config)

    return _g_singletonCloudlet

################################################################################################################
# Singleton that will contain common resources: config values, db connections, common managers.
################################################################################################################
class Cloudlet(object):

    ################################################################################################################
    # Constructor, should be called only once, independent on how many apps there are.
    ################################################################################################################    
    def __init__(self, config, *args, **kwargs):
        print 'Loading cloudlet configuration...'

        # DB information.
        host = config['pycloud.mongo.host']
        port = int(config['pycloud.mongo.port'])
        dbName = config['pycloud.mongo.db']

        try:
            self.conn = Connection(host, port)
        except ConnectionFailure as error:
            print error
            raise Exception('Unable to connect to MongoDB')

        self.db = self.conn[dbName]
            
        # Get information about folders to be used.
        self.svmCache = config['pycloud.servicevm.cache']
        self.svmInstancesFolder = config['pycloud.servicevm.instances_folder']
        self.appFolder = config['pycloud.push.app_folder']
        
        # Load the templates to be used when creating VMs.
        self.newVmFolder = config['pycloud.servicevm.new_folder']        
        self.newVmWinXml = config['pycloud.servicevm.win_xml_template']
        self.newVmLinXml = config['pycloud.servicevm.lin_xml_template']

        # New config params
        self.svm_temp_folder = config['pycloud.servicevm.instances_folder']
        self.service_cache = config['pycloud.servicevm.cache']



        # TODO: this introduces an ungly circular dependency...
        # TODO: self.instanceManager should be removed
        # Create the ServiceVM Instance Manager, which will be used by several apps.
        self.instanceManager = instancemanager.ServiceVMInstanceManager(self)

        print 'cloudlet created.'


    @staticmethod
    def system_information():
        return Cloudlet_Metadata()

    def cleanup_system(self):
        destroy_all_vms()
        self._clean_instances_folder()
        self._remove_service_vms()
        portmanager.PortManager.clearPorts()

    def _clean_instances_folder(self):
        print 'Cleaning up \'%s\'' % self.svm_temp_folder
        if os.path.exists(self.svm_temp_folder):
            print '\tDeleting all files in \'%s\'' % self.svm_temp_folder
            shutil.rmtree(self.svm_temp_folder)
        if not os.path.exists(self.svm_temp_folder):
            print '\tMaking folder \'%s\'' % self.svm_temp_folder
            os.makedirs(self.svm_temp_folder)
        print 'Done cleaning up \'%s\'' % self.svm_temp_folder

    def _remove_service_vms(self):
        from pycloud.pycloud.model import ServiceVM
        ServiceVM._collection.drop()




class Cpu_Info(model.AttrDict):

    def __init__(self):
        self.max_cores = psutil.cpu_count()
        self.usage = psutil.cpu_percent(interval=0.1)


class Memory_Info(model.AttrDict):

    def __init__(self):
        mem = psutil.virtual_memory()
        self.max_memory = mem.total
        self.free_memory = mem.free


class Cloudlet_Metadata(model.AttrDict):

    def __init__(self):
        self.memory_info = Memory_Info()
        self.cpu_info = Cpu_Info()