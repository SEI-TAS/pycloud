__author__ = 'jdroot'

from pymongo import Connection
from pymongo.errors import ConnectionFailure
from pycloud.pycloud.servicevm import instancemanager
from pycloud.pycloud.mongo.model import AttrDict
import psutil
import os

# Singleton object to maintain intra- and inter-app variables.
g_singletonCloudlet = None

################################################################################################################
# Creates the Cloudlet singleton, or gets an instance of it if it had been already created.
################################################################################################################
def get_cloudlet_instance(config):    
    # Only create it if we don't have a reference already.
    global g_singletonCloudlet
    if(g_singletonCloudlet == None):
        print 'Creating Cloudlet singleton.'
        g_singletonCloudlet = Cloudlet(config)

    return g_singletonCloudlet

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



        # TODO: this introduces an ungly circular dependency...
        # Create the ServiceVM Instance Manager, which will be used by several apps.
        self.instanceManager = instancemanager.ServiceVMInstanceManager(self)

    def system_information(self):
        return Cloudlet_Metadata()


class Cpu_Info(AttrDict):

    def __init__(self):
        self.max_cores = psutil.cpu_count()
        self.usage = psutil.cpu_percent(interval=0.1)


class Memory_Info(AttrDict):

    def __init__(self):
        mem = psutil.virtual_memory()
        self.max_memory = mem.total
        self.free_memory = mem.free


class Cloudlet_Metadata(AttrDict):

    def __init__(self):
        self.memory_info = Memory_Info()
        self.cpu_info = Cpu_Info()