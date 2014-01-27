__author__ = 'jdroot'

from pylons.controllers import WSGIController
from pylons import config

# Creating this just to have it for the future
class BaseController(WSGIController):

    def __before__(self):
        self.pre()

    def __after__(self):
        self.post()

    def pre(self):
        pass

    def post(self):
        pass