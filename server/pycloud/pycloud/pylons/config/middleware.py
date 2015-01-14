"""Pylons middleware initialization"""
import importlib

from pylons.wsgiapp import PylonsApp
from routes.middleware import RoutesMiddleware
from paste.registry import RegistryManager
from paste.cascade import Cascade
from paste.urlparser import StaticURLParser

# Get the object that has the config information from the main config file.
from pylons import config

###########################################################################################################################
# Generic WSGI app appropriate for Cloudlets. Can be used by different actual apps.
###########################################################################################################################
class CloudletApp(PylonsApp):
    # Used to store the name of the module that stores the controllers for this particular app.
    controllers_module = ""

    # Constructor.
    def __init__(self, controllers_module, *args, **kwargs):
        self.controllers_module = controllers_module
        super(CloudletApp, self).__init__(*args, **kwargs)
        self._controllers = None

    # @Overriding.        
    # Sets up the environment for the WSGI app, and loads its controllers.
    # Called by the HTTP server each time a new request is received, before dispatching the request.
    def setup_app_env(self, environ, start_response):
        PylonsApp.setup_app_env(self, environ, start_response)
        self.load_controllers()

    # Loads the controllers from the controllers module previously setup in the constructor.
    def load_controllers(self):
        # If we have already loaded the controllers, do no reload them.
        if self._controllers:
            return

        # Gets the controller module itself, make it load its controllers, and store a reference to the module.
        controllers = importlib.import_module(self.controllers_module)
        controllers.load_controllers()
        self._controllers = controllers

    # @Overriding.
    # Returns a particular controller from the controllers module given its name.
    # Automatically called by HTTP server when dispatching a request.
    def find_controller(self, controller_name):
        # Return the controller from the cache, if it has been cached before.
        if controller_name in self.controller_classes:
            return self.controller_classes[controller_name]

        # Get the controller from the controllers module.
        controller_cls = self._controllers.get_controller(controller_name)

        # Cache loaded controllers.
        self.controller_classes[controller_name] = controller_cls
        return controller_cls
        
###########################################################################################################################
# Generic function used to create a WSGI app.
###########################################################################################################################
def generic_make_app(make_map_function, controllers_module, root_path, global_conf, full_stack=True, static_files=True, **app_conf):
    # Configure the Pylons environment.
    from pycloud.pycloud.pylons.config.environment import load_environment    
    load_environment(make_map_function, root_path, global_conf, app_conf)

    # Create the base app, and wrap it in middleware.
    app = CloudletApp(controllers_module)
    app = RoutesMiddleware(app, config["routes.map"])
    app = RegistryManager(app)

    # Create the sub-app to serve static files.
    static_app = StaticURLParser(config['pylons.paths']['static_files'])

    # Set up the order apps are resolved (static and the main one).
    app = Cascade([static_app, app])

    return app
