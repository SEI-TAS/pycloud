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
__author__ = 'Sebastian'

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.manager.lib.pages import DevicesPage

from pycloud.pycloud.model.deployment import Deployment
from pycloud.pycloud.model.paired_device import PairedDevice

################################################################################################################
# Controller for the page.
################################################################################################################
class DevicesController(BaseController):

    ############################################################################################################
    # Lists the stored devices, and allows to reset or to add more.
    ############################################################################################################
    def GET_list(self):
        page = DevicesPage()

        # Get the overall deployment info.
        page.deployment = Deployment.find_one()

        # Get the paired devices.
        page.paired_devices = PairedDevice.find()

        return page.render()

    ############################################################################################################
    #
    ############################################################################################################
    def GET_bootstrap(self):
        return ''

    ############################################################################################################
    #
    ############################################################################################################
    def GET_unpair(self):
        return ''

    ############################################################################################################
    #
    ############################################################################################################
    def GET_revoke(self):
        return ''
