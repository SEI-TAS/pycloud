
__author__ = 'jdroot'

from pylons import config
from pycloud.pycloud.pylons.lib.app_globals import Globals
from pycloud.pycloud.pylons.lib import helpers
from mako.lookup import TemplateLookup
import os


def load_environment(make_map_function, root_path, global_conf={}, app_conf={}):

    paths = {'root': root_path,
             'controllers': os.path.join(root_path, 'controllers'),
             'templates': [os.path.join(root_path, 'templates')],
             'static_files': os.path.join(root_path, 'public')
    }
    
    print 'Templates path: ' + os.path.join(root_path, 'templates')

    config.init_app(global_conf, app_conf, package='pycloud', paths=paths)

    config['routes.map'] = make_map_function()
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