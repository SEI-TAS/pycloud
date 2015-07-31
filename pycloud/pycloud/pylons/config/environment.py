# KVM-based Discoverable Cloudlet (KD-Cloudlet) 
# Copyright (c) 2015 Carnegie Mellon University.
# All Rights Reserved.
# 
# THIS SOFTWARE IS PROVIDED "AS IS," WITH NO WARRANTIES WHATSOEVER. CARNEGIE MELLON UNIVERSITY EXPRESSLY DISCLAIMS TO THE FULLEST EXTENT PERMITTEDBY LAW ALL EXPRESS, IMPLIED, AND STATUTORY WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT OF PROPRIETARY RIGHTS.
# 
# Released under a modified BSD license, please see license.txt for full terms.
# DM-0002138
# 
# KD-Cloudlet includes and/or makes use of the following Third-Party Software subject to their own licenses:
# MiniMongo
# Copyright (c) 2010-2014, Steve Lacy 
# All rights reserved. Released under BSD license.
# https://github.com/MiniMongo/minimongo/blob/master/LICENSE
# 
# Bootstrap
# Copyright (c) 2011-2015 Twitter, Inc.
# Released under the MIT License
# https://github.com/twbs/bootstrap/blob/master/LICENSE
# 
# jQuery JavaScript Library v1.11.0
# http://jquery.com/
# Includes Sizzle.js
# http://sizzlejs.com/
# Copyright 2005, 2014 jQuery Foundation, Inc. and other contributors
# Released under the MIT license
# http://jquery.org/license

__author__ = 'jdroot'

from pycloud.pycloud.pylons.lib.app_globals import Globals
from pycloud.pycloud.pylons.lib import helpers
from mako.lookup import TemplateLookup
from pylons.configuration import PylonsConfig
import os


def load_environment(make_map_function, root_path, global_conf={}, app_conf={}):

    paths = {'root': root_path,
             'controllers': os.path.join(root_path, 'controllers'),
             'templates': [os.path.join(root_path, 'templates')],
             'static_files': os.path.join(root_path, 'public')
    }
    
    print 'Templates path: ' + os.path.join(root_path, 'templates')

    config = PylonsConfig()

    config.init_app(global_conf, app_conf, package='pycloud', paths=paths)

    config['routes.map'] = make_map_function(config)
    config['pylons.app_globals'] = Globals(config)
    config['debug'] = True
    config['pylons.h'] = helpers

    # For backwards compat with 0.9.7. This prevents errors from showing up when attributes from c that do not exist
    # are used.
    config['pylons.strict_tmpl_context'] = False

    # Clean up the system. This must be called after the object is already created
    config['pylons.app_globals'].cloudlet.cleanup_system()

    # Set up environment for all mako templates.
    config["pylons.app_globals"].mako_lookup = TemplateLookup(
        directories=paths["templates"],
        input_encoding="utf-8",
        imports=[
            "from pylons import tmpl_context as c, app_globals, request",
            "from pylons.i18n import _, ungettext",
            "from pycloud.pycloud.pylons.lib import helpers as h"
            ]
    )

    return config
