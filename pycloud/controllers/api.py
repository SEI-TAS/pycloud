__author__ = 'jdroot'

from pycloud.lib.base import BaseController
from util import asjson

class ApiController(BaseController):

    @asjson
    def list_services(self):
        coll = self.db['serviceInfo']

        #Only return specific attributes
        ret = coll.find({}, {
            "_id": 1,
            "description": 1,
            "tags": 1,
            "servicePort": 1
        })
        return ret