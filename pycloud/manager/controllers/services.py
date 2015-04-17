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

import logging

from pylons import request, response, session, tmpl_context as c, url

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.manager.lib.pages import ServicesPage
from pycloud.pycloud.model import Service

from pycloud.pycloud.utils import ajaxutils
from pycloud.pycloud.pylons.lib.util import asjson

log = logging.getLogger(__name__)

################################################################################################################
# Controller for the Services page.
################################################################################################################
class ServicesController(BaseController):

    ############################################################################################################
    # Entry point.
    ############################################################################################################
    def GET_index(self):
        return self.GET_listServices()

    ############################################################################################################
    # Shows the list of cached Services.
    ############################################################################################################
    def GET_listServices(self):
        # Mark the active tab.
        c.services_active = 'active'
    
        # Get a list of existing stored VMs in the cache.
        services = Service.find()
        
        # Pass the grid and render the page.
        servicesPage = ServicesPage()
        # servicesPage.servicesGrid = servicesGrid
        servicesPage.services = services

        return servicesPage.render()
        
    ############################################################################################################
    # Shows the list of cached Services.
    ############################################################################################################
    @asjson
    def GET_removeService(self, id):
        try:
            service = Service.find_and_remove(id)
            if service:
                service.destroy(force=True)
        except Exception as e:
            # If there was a problem removing the service, return that there was an error.
            msg = 'Error removing Service: ' + str(e)
            return ajaxutils.show_and_return_error_dict(msg)
        
        # Everything went well.
        return ajaxutils.JSON_OK