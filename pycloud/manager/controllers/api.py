__author__ = 'jdroot'

from pycloud.manager.lib.base import BaseController
from pycloud.manager.controllers.util import asjson


class ApiController(BaseController):

    """
    Return all services this cloudet offers
    """
    @asjson
    def GET_list_services(self):
        return self.cloudlet.get_services()

