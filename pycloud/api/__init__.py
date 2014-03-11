
import os
from pycloud.api.config import routing

def make_app(*args, **kwargs):
    from pycloud.pycloud.pylons.config.middleware import make_app as _make_app
    controllers_module = "pycloud.api.controllers"
    root_path = os.path.dirname(os.path.abspath(__file__))
    return _make_app(routing.make_map, controllers_module, root_path, *args, **kwargs)