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

controllers = {}

#Return a controller by name, error if no controller is found
def get_controller(name):
    name = name.lower() + 'controller'
    if name in controllers:
        return controllers[name]
    else:
        raise KeyError('Controller ' + name + ' was not found.')

# Define all of our controllers by importing them
def load_controllers():

    # Import All Controllers Here
    
    # Cloudlet Server API controllers.
    from pycloud.api.controllers.services import ServicesController
    from pycloud.api.controllers.servicevm import ServiceVMController
    from pycloud.api.controllers.apppush import AppPushController
    from pycloud.api.controllers.cloudlet import CloudletController
    from pycloud.api.controllers.encrypted import EncryptedController

    # Cache the controllers in a look up map
    controllers.update((name.lower(), obj) for name, obj in locals().iteritems())