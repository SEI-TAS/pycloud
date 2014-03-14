__author__ = 'jdroot'

from pymongo import Connection
from pymongo.errors import ConnectionFailure

class Cloudlet(object):

    def __init__(self, config, *args, **kwargs):
    
        print 'Loading cloudlet configuration...'

        # DB information.
        host = config['pycloud.mongo.host']
        port = int(config['pycloud.mongo.port'])
        db = config['pycloud.mongo.db']

        try:
            self.conn = Connection(host, port)
        except ConnectionFailure as error:
            print error
            raise Exception('Unable to connect to MongoDB')
            
        # Get information about folders to be used.
        self.svmCache = config['pycloud.servicevm.cache']
        self.svmInstancesFolder = config['pycloud.servicevm.instances_folder']
        self.appFolder = config['pycloud.push.app_folder']
        
        # Load the templates to be used when creating VMs.
        self.newVmFolder = config['pycloud.servicevm.new_folder']        
        self.newVmWinXml = config['pycloud.servicevm.win_xml_template']
        self.newVmLinXml = config['pycloud.servicevm.lin_xml_template']

    def get_services(self):

        coll = self.db['serviceInfo']
        #Only return specific attributes
        return coll.find({}, {
            "_id": 1,
            "description": 1,
            "tags": 1,
        })