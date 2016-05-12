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

from pylons import request
from pylons import response, session, tmpl_context as c
from pylons import app_globals

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.manager.lib.pages import InstancesPage
from pycloud.pycloud.model import Service, ServiceVM, PairedDevice
from pycloud.pycloud.pylons.lib.util import asjson

from pycloud.pycloud.utils import ajaxutils
from pycloud.pycloud.network import wifi, finder
from pycloud.pycloud.network.wifi import WifiManager
from pycloud.pycloud.cloudlet import Cloudlet
from pycloud.pycloud.model import migrator

log = logging.getLogger(__name__)

################################################################################################################
# Controller for the ServiceVMs Instances page.
################################################################################################################
class InstancesController(BaseController):

    ############################################################################################################
    # Shows the list of running Service VM instances.
    ############################################################################################################
    def GET_index(self):
        # Mark the active tab.
        c.servicevms_active = 'active'
        svms = ServiceVM.find()

        # Setup the page to render.
        instancesPage = InstancesPage()
        instancesPage.svms = svms

        # Get the current connection.
        current_network = WifiManager.current_network(interface=app_globals.cloudlet.wifi_adapter)
        instancesPage.current_network = current_network

        # Pass the grid and render the page.
        return instancesPage.render()


    ############################################################################################################
    # Returns a list of available wifi networks.
    ############################################################################################################
    @asjson
    def GET_get_available_networks(self):
        # Get a list of cloudlet networks in range, and pass them to dict format.
        available_networks_array = WifiManager.list_networks()
        available_networks = {}
        for network_id in available_networks_array:
            available_networks[network_id] = False

        # Mark our current network as connected.
        current_network = WifiManager.current_network(interface=app_globals.cloudlet.wifi_adapter)
        if current_network in available_networks:
            available_networks[current_network] = True

        print 'Available networks: '
        print available_networks

        return available_networks

    ############################################################################################################
    # Returns a list of cloudlets available in our current network (or networks).
    ############################################################################################################
    @asjson
    def GET_get_available_cloudlets(self):
        # Get a list of cloudlets in our current network.
        cloudlet_finder = finder.CloudletFinder()
        cloudlets = cloudlet_finder.find_cloudlets(seconds_to_wait=2)

        # Filter out ourselves from the list of cloudlets.
        current_cloudlet = Cloudlet.get_fqdn()
        print 'Current cloudlet: ' + current_cloudlet
        if current_cloudlet in cloudlets:
            del cloudlets[current_cloudlet]

        # Encode name, port and encryption info into string to be shown to user.
        cloudlet_info_dict = {}
        for cloudlet_name in cloudlets:
            cloudlet_info = cloudlets[cloudlet_name]
            encoded_cloudlet_info = cloudlet_name + ":" + str(cloudlet_info.port) + ":encryption-" + cloudlet_info.encryption
            cloudlet_info_dict[encoded_cloudlet_info] = encoded_cloudlet_info

        print 'Available cloudlets: '
        print cloudlet_info_dict

        return cloudlet_info_dict

    ############################################################################################################
    # Starts a new SVM instance of the Service.
    ############################################################################################################
    @asjson
    def GET_startInstance(self, id):
        # Look for the service with this id
        service = Service.by_id(id)
        if service:
            clone_full_image = False
            if request.params.get('clone_full_image'):
                clone_full_image = True

            svm = None
            try:
                # Get a ServiceVM instance
                svm = service.get_vm_instance(clone_full_image=clone_full_image)
                return svm
            except Exception as e:
                if svm:
                    # If there was a problem starting the instance, return that there was an error.
                    svm.stop()
                msg = 'Error starting Service VM Instance: ' + str(e)
                return ajaxutils.show_and_return_error_dict(msg)
        else:
            msg = 'Service {} not found.'.format(id)
            return ajaxutils.show_and_return_error_dict(msg)

    ############################################################################################################
    # Stops an existing instance.
    ############################################################################################################
    @asjson
    def GET_stopInstance(self, id):
        try:    
            # Stop an existing instance with the given ID.
            svm = ServiceVM.by_id(id)
            svm.stop()
        except Exception as e:
            # If there was a problem stopping the instance, return that there was an error.
            msg = 'Error stopping Service VM Instance: ' + str(e)
            return ajaxutils.show_and_return_error_dict(msg)

        # Everything went well.
        return ajaxutils.JSON_OK

    ############################################################################################################
    # Command to migrate a machine.
    ############################################################################################################
    @asjson
    def GET_migrateInstance(self, id):
        try:
            remote_host_info = request.params.get('target', None).split(':')
            remote_host = remote_host_info[0] + ':' + remote_host_info[1]
            encrypted = True if remote_host_info[2] == 'encryption-enabled' else False
            migrator.migrate_svm(id, remote_host, encrypted)
        except Exception, e:
            msg = 'Error migrating: ' + str(e)
            import traceback
            traceback.print_exc()

            return ajaxutils.show_and_return_error_dict(msg)

        return ajaxutils.JSON_OK

    ############################################################################################################
    # Returns a list of running svms.
    ############################################################################################################    
    @asjson    
    def GET_svmList(self):
        try:    
            # Get the list of running instances.
            svm_list = ServiceVM.find()
            return svm_list
        except Exception as e:
            # If there was a problem stopping the instance, return that there was an error.
            msg = 'Error getting list of instance changes: ' + str(e)
            return ajaxutils.show_and_return_error_dict(msg)

    ############################################################################################################
    #
    ############################################################################################################
    @asjson
    def GET_wifiConnect(self):
        ssid = request.params.get('target')

        try:
            WifiManager.connect_to_network(ssid)
            return ajaxutils.JSON_OK
        except Exception as e:
            msg = 'Error connecting to Wi-Fi network {}: {}'.format(ssid, str(e))
            return ajaxutils.show_and_return_error_dict(msg)


    ############################################################################################################
    #
    ############################################################################################################
    @asjson
    def GET_wifiDisconnect(self):
        try:
            WifiManager.disconnect_from_network()
            return ajaxutils.JSON_OK
        except Exception as e:
            msg = 'Error disconnecting from Wi-Fi network {}: {}'.format(ssid, str(e))
            return ajaxutils.show_and_return_error_dict(msg)
