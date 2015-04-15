
import os

# Gets general parameters and calls function to create the WSGI app.
# This will be called automatically by Pylons when creating the app.
def make_app(*args, **kwargs):
    # Arguments needed to make some lower level functions more generic to be used in multiple apps.
    from pycloud.api.config import routing
    controllers_module = "pycloud.api.controllers"
    root_path = os.path.dirname(os.path.abspath(__file__))
    
    # Get the generic function to make the app, passing the particular arguments for this app.
    print "Setting up WSGI environment for API app"
    from pycloud.pycloud.pylons.config.middleware import generic_make_app
    return generic_make_app(routing.make_map, controllers_module, root_path, *args, **kwargs)