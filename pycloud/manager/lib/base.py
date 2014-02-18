__author__ = 'jdroot'

from pylons.controllers import WSGIController
from pylons import c, g, request, response

# Creating this just to have it for the future
class BaseController(WSGIController):

    def __call__(self, environ, start_response):
        action = request.environ['pylons.routes_dict'].get('action')
        if action:
            method = request.method.upper()
            if method == 'HEAD':
                method = 'GET'

            handler_name = method + '_' + action

            request.environ['pylons.routes_dict']['action_name'] = action
            request.environ['pylons.routes_dict']['action'] = handler_name

        ret = WSGIController.__call__(self, environ, start_response)
        return ret

    def __before__(self):
        # Make the database available on every request
        self.cloudlet = g.cloudlet
        self.pre()

    def __after__(self):
        self.post()

    def pre(self):
        pass

    def post(self):
        pass