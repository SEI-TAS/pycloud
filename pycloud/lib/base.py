__author__ = 'jdroot'

from pylons.controllers import WSGIController
from pylons import config
from pylons import g

# Creating this just to have it for the future
class BaseController(WSGIController):

    def __call__(self, environ, start_response):
        # Make the database available on every request
        self.db = g.db
        return WSGIController.__call__(self, environ, start_response)

    def __before__(self):
        self.pre()

    def __after__(self):
        self.post()

    def pre(self):
        pass

    def post(self):
        pass