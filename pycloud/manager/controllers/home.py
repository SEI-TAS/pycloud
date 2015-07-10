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
from pycloud.manager.lib.pages import HomePage
from pycloud.manager.lib.auth import render_signin

from pycloud.pycloud.cloudlet import Cloudlet
from pycloud.pycloud.pylons.lib.util import asjson

log = logging.getLogger(__name__)

################################################################################################################
# Controller for the main page.
################################################################################################################
class HomeController(BaseController):

    ############################################################################################################
    # Shows the main page.  
    ############################################################################################################
    def GET_index(self):
        # Mark the active tab.
        c.home_active = 'active'

        # Get current metadata.
        page = HomePage()
        ret = Cloudlet.system_information()
        page.machine_status = ret

        # Render the page with the grid.
        return page.render()

    ############################################################################################################
    # Returns the cloudlet state.
    ############################################################################################################
    @asjson
    def GET_state(self):
        machine_state = Cloudlet.system_information()
        return machine_state

    ############################################################################################################
    # Shows the sign in page when signing out.
    ############################################################################################################
    def GET_signout(self):
        return render_signin()
