__author__ = 'jdroot'

from pycloud.lib.base import BaseController
from pycloud.controllers.util import asjson

from routes import url_for

class ApiController(BaseController):

    """
    Return all services this cloudet offers
    """
    @asjson
    def GET_list_services(self):
        coll = self.db['serviceInfo']
        #Only return specific attributes
        return coll.find({}, {
            "_id": 1,
            "description": 1,
            "tags": 1,
        })

