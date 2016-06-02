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

from zeroconf import ServiceBrowser, Zeroconf
import time

#######################################################################################################################
# Finds cloudlets through Zeroconf.
#######################################################################################################################
class CloudletFinder(object):
    # DNS-SD identifier for cloudlets.
    CLOUDLET_SERVICE_DNS = '_cloudlet._tcp.local.'

    ####################################################################################################################
    # Constructor.
    ####################################################################################################################
    def __init__(self):
        self.services = {}

    ####################################################################################################################
    # Finds cloudlets and returns a list.
    ####################################################################################################################
    def find_cloudlets(self, seconds_to_wait=3):
        print 'Started looking for cloudlets'
        self.services = {}
        zeroconf = Zeroconf()
        browser = ServiceBrowser(zeroconf, CloudletFinder.CLOUDLET_SERVICE_DNS, listener=self)

        # Wait to find cloudlets.
        print 'Waiting for results'
        time.sleep(seconds_to_wait)

        # Stop looking for cloudlets.
        browser.cancel()

        # Return the list of cloudlets found.
        print 'Cloudlets found: '
        print self.services
        return self.services

    ####################################################################################################################
    # Called when a new service is found, adds it to a list of services.
    ####################################################################################################################
    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info is None:
            print("Empty service was registered; ignoring it.")
            return

        print("Service added, service name: %s" % name)
        self.services[info.server] = info

        # Move encryption state to specific property for easier access.
        encryption = ''
        if 'encryption' in info.properties:
            encryption = info.properties['encryption']
        self.services[info.server].encryption = encryption

    ####################################################################################################################
    # Called when a service is removed, removes it from a list of services.
    ####################################################################################################################
    def remove_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        print("Service %s removed, service info: %s" % (name, info))
        del self.services[info.server]
