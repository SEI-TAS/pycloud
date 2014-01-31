__author__ = 'jdroot'

from pylons import config
from pycloud.lib.app_globals import Globals
from pycloud.lib import helpers
from mako.lookup import TemplateLookup
import routing
import os

def load_enviroment(global_conf={}, app_conf={}):

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