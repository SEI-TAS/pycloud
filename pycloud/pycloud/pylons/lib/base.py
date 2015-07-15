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

from pylons.controllers import WSGIController
from pylons import app_globals, request, session
from pylons import config

from pycloud.manager.lib import auth

# Creating this just to have it for the future
class BaseController(WSGIController):

    def __call__(self, environ, start_response):
        action = request.environ['pylons.routes_dict'].get('action')
        if action:
            method = request.method.upper()
            if method == 'HEAD':
                method = 'GET'

            handler_name = method + '_' + action

            #request.environ['pylons.routes_dict']['action_name'] = action
            request.environ['pylons.routes_dict']['action'] = handler_name

        ret = WSGIController.__call__(self, environ, start_response)
        return ret

    def __before__(self):
        # Only check authentication if we are not the authentication controller.
        if type(self).__name__ != config['pycloud.auth']:
            # Ensure authentication.
            auth.ensure_authenticated()

        # Make the database available on every request
        self.cloudlet = app_globals.cloudlet
        self.pre()

    def __after__(self):
        self.post()

    def pre(self):
        pass

    def post(self):
        pass

# Get a boolean from a request param
def bool_param(name, default=False):
    ret = request.params.get(name, default)
    if not isinstance(ret, bool):
        ret = ret.upper() in ['T', 'TRUE', 'Y', 'YES']
    return ret