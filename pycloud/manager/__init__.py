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

import os

from pycloud.manager.config import routing
from pycloud.pycloud.pylons.config.middleware import generic_make_app

# Gets general parameters and calls function to create the WSGI app.
# This will be called automatically by Pylons when creating the app.
def make_app(global_conf, **app_conf):
    # Arguments needed to make some lower level functions more generic to be used in multiple apps.
    controllers_module = "pycloud.manager.controllers"
    root_path = os.path.dirname(os.path.abspath(__file__))

    # Get the generic function to make the app, passing the particular arguments for this app.
    print "Setting up WSGI environment for Manager app"
    app = generic_make_app(routing.make_map, controllers_module, root_path, global_conf, **app_conf)

    return app
