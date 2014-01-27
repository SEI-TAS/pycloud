__author__ = 'jdroot'

from pycloud.lib.base import BaseController

class ApiController(BaseController):

    def home(self):
        return "Hello World"