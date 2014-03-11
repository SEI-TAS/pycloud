__author__ = 'jdroot'

from pymongo import Connection
from pymongo.errors import ConnectionFailure

class Cloudlet(object):

    def __init__(self, config, *args, **kwargs):

        host = config['pycloud.mongo.host']
        port = int(config['pycloud.mongo.port'])
        db = config['pycloud.mongo.db']

        try:
            self.conn = Connection(host, port)
        except ConnectionFailure as error:
            print error
            raise Exception('Unable to connect to MongoDB')

    def get_services(self):

        coll = self.db['serviceInfo']
        #Only return specific attributes
        return coll.find({}, {
            "_id": 1,
            "description": 1,
            "tags": 1,
        })