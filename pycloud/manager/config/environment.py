from pycloud.manager.config import routing

__author__ = 'jdroot'

from pylons import config
from pycloud.manager.lib.app_globals import Globals
from pycloud.manager.lib import helpers
from mako.lookup import TemplateLookup
import os

def load_environment(global_conf={}, app_conf={}):
#def load_environment(global_conf, app_conf):

    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    paths = {'root': root_path,
             'controllers': os.path.join(root_path, 'controllers'),
             'templates': [os.path.join(root_path, 'templates')],
             'static_files': os.path.join(root_path, 'public')
    }

    config.init_app(global_conf, app_conf, package='pycloud', paths=paths)

    config['routes.map'] = routing.make_map()
    config['debug'] = True
    config['pylons.g'] = Globals()
    config['pylons.h'] = helpers


    config["pylons.g"].mako_lookup = TemplateLookup(
        directories=paths["templates"],
        input_encoding="utf-8",
        imports=[
            "from pylons import c, g, request",
            "from pylons.i18n import _, ungettext",
            ]
    )