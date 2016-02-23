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
import json
import os

# External library for creating HTTP requests.
import requests

from pylons import request
from pylons import response, session, tmpl_context as c
from pylons.controllers.util import abort
from pylons import app_globals

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.manager.lib.pages import InstancesPage
from pycloud.pycloud.model import Service, ServiceVM, PairedDevice
from pycloud.pycloud.pylons.lib.util import asjson

from pycloud.pycloud.utils import fileutils

from pycloud.pycloud.utils import ajaxutils
from pycloud.pycloud.network import wifi, finder
from pycloud.pycloud.cloudlet import Cloudlet

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
        wifi_manager = wifi.WifiManager()
        wifi_manager.interface = 'wlan0'
        instancesPage.current_network = wifi_manager.current_network()

        # Get a list of paired cloudlet networks in range.
        available_networks = wifi_manager.list_networks()
        paired_networks = PairedDevice.by_type('cloudlet')
        paired_networks_in_range = {}
        for paired_network in paired_networks:
            if paired_network.connection_id in available_networks:
                paired_networks_in_range[paired_network.connection_id] = paired_network.connection_id

        # Filter out ourselves.
        current_network = wifi_manager.current_network()
        if current_network in paired_networks_in_range:
            del paired_networks_in_range[current_network]

        instancesPage.available_networks = paired_networks_in_range
        instancesPage.network = current_network

        # Get a list of cloudlets in our current networks.
        cloudlet_finder = finder.CloudletFinder()
        cloudlets = cloudlet_finder.find_cloudlets()

        # Filter out ourselves from the list of cloudlets.
        current_cloudlet = Cloudlet.get_hostname()
        if current_cloudlet in cloudlets:
            cloudlets.remove(current_cloudlet)

        # Show only paired cloudlets.
        paired_cloudlets = []
        for paired_cloudlet in paired_networks:
            if paired_cloudlet.device_id in cloudlets:
                paired_cloudlets.append(paired_cloudlet)
        instancesPage.available_cloudlets = paired_cloudlets

        # Pass the grid and render the page.
        return instancesPage.render()

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

            # Get a ServiceVM instance
            svm = service.get_vm_instance(clone_full_image=clone_full_image)
            try:
                # Start the instance, if it works, save it and return ok
                svm.start()
                svm.save()
                return svm
            except Exception as e:
                # If there was a problem starting the instance, return that there was an error.
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
            svm = ServiceVM.find_and_remove(id)
            svm.destroy()
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
            # Parse the body of the request as JSON into a python object.
            # First remove URL quotes added to string, and then remove trailing "=" (no idea why it is there).
            #parsedJsonString = urllib.unquote(request.body)[:-1]
            #fields = json.loads(parsedJsonString)

            # The host we are migrating to.
            remote_host = request.params.get('target', None)

            # Find the SVM.
            svm = ServiceVM.by_id(id)
            print 'VM found: ' + str(svm)

            # TODO: assuming remote cloudlet is listening on same port as local cloudlet.
            api_port = app_globals.cloudlet.api_port
            print 'Migrating to remote cloudlet: ' + remote_host
            remote_http_host = 'http://%s:%s' % (remote_host, api_port)

            # Transfer the metadata.
            print 'Starting metadata file transfer...'
            remote_url = '%s/instances/receiveMigratedSVMMetadata' % remote_http_host
            payload = json.dumps(svm)
            headers = {'content-type': 'application/json'}
            result = requests.post(remote_url, data=payload, headers=headers)
            if result.status_code != requests.codes.ok:
                raise Exception('Error transferring metadata.')
            print 'Metadata was transferred: ' + str(result)

            # We pause the VM before transferring its disk and memory state.
            print 'Pausing VM...'
            result = svm.pause()
            if result == -1:
                raise Exception("Cannot pause VM: %s", str(id))
            print 'VM paused.'

            # Ensure we own the image file to migrate.
            fileutils.chown_to_current_user(svm.vm_image.disk_image)

            # Transfer the disk image file.
            print 'Starting disk image file transfer...'
            disk_image_full_path = os.path.abspath(svm.vm_image.disk_image)
            remote_url = '%s/instances/receiveMigratedSVMDiskFile' % remote_http_host
            payload = {'id': id}
            files = {'disk_image_file': open(disk_image_full_path, 'rb')}
            result = requests.post(remote_url, data=payload, files=files)
            if result.status_code != requests.codes.ok:
                raise Exception('Error transferring disk image file.')
            print 'Disk image file was transferred: ' + str(result)

            # Do the memory state migration.
            print 'Migrating through libvirt to ' + remote_host
            svm.migrate(remote_host, p2p=False)
            # TODO: if migration fails, ask remote to remove svm.

            # Notify remote cloudlet that migration finished.
            print 'Telling target cloudlet that migration has finished.'
            remote_url = '%s/instances/resumeMigratedSVM' % remote_http_host
            payload = {'id': id}
            result = requests.post(remote_url, data=payload)
            if result.status_code != requests.codes.ok:
                raise Exception('Error notifying migration end.')
            print 'Cloudlet notified: ' + str(result)

            # Remove the local VM.
            svm = ServiceVM.find_and_remove(id)
            svm.destroy()
        except Exception, e:
            msg = 'Error migrating: ' + str(e)
            import traceback
            traceback.print_exc()

            return ajaxutils.show_and_return_error_dict(msg)

        return ajaxutils.JSON_OK

    ############################################################################################################
    # Receives information about a migrated VM.
    ############################################################################################################
    @asjson
    def POST_receiveMigratedSVMMetadata(self):
        # Parse the body of the request as JSON into a python object.
        json_svm = json.loads(request.body)

        # Get information about the SVM.
        print 'Obtaining metadata of SVM to be received.'
        migrated_svm = ServiceVM()
        migrated_svm._id = json_svm['_id']
        migrated_svm.vm_image = json_svm['vm_image']
        migrated_svm.port_mappings = json_svm['port_mappings']
        migrated_svm.service_port = json_svm['service_port']
        migrated_svm.port = json_svm['port']
        migrated_svm.ip_address = json_svm['ip_address']
        migrated_svm.mac_address = json_svm['mac_address']
        migrated_svm.ssh_port = json_svm['ssh_port']
        migrated_svm.vnc_address = json_svm['vnc_address']
        migrated_svm.service_id = json_svm['service_id']
        migrated_svm.fqdn = json['fqdn']

        # Update network data, especially needed in non-bridged mode.
        migrated_svm.update_migrated_network()

        # Save to internal DB.
        migrated_svm.save()
        print 'SVM metadata stored.'

        return ajaxutils.JSON_OK

    ############################################################################################################
    # Receives the disk image file of a migrated SVM.
    ############################################################################################################
    @asjson
    def POST_receiveMigratedSVMDiskFile(self):
        # Get the id and load the metadata for this SVM.
        svm_id = request.params.get('id')
        migrated_svm = ServiceVM.by_id(svm_id)
        if not migrated_svm:
            abort(404, '404 Not Found - SVM with id %s not found' % svm_id)

        # Receive the transferred file and update its path.
        print 'Storing disk image file of SVM in migration.'
        destination_folder = os.path.join(app_globals.cloudlet.svmInstancesFolder, svm_id)
        disk_image_object = request.params.get('disk_image_file').file
        migrated_svm.vm_image.store(destination_folder, disk_image_object)
        print 'Migrated SVM disk image file stored.'

        # Check that we have the backing file, and rebase the new file so it will point to the correct backing file.
        service = Service.by_id(migrated_svm.service_id)
        if service:
            print 'Rebasing backing file for service %s.' % migrated_svm.service_id
            backing_disk_file = service.vm_image.disk_image
            migrated_svm.vm_image.rebase_disk_image(backing_disk_file)
        else:
            # Migration will be unsuccessful since we won't have the backing file.
            print 'Service %s not found in local cloudlet.' % migrated_svm.service_id
            abort(500, '500 Server Error - Service is not installed on target cloudlet.')

        # Save to internal DB.
        migrated_svm.save()

        return ajaxutils.JSON_OK

    ############################################################################################################
    # Receives information about a migrated VM.
    ############################################################################################################
    @asjson
    def POST_resumeMigratedSVM(self):
        # Find the SVM.
        svm_id = request.params.get('id')
        migrated_svm = ServiceVM.by_id(svm_id)
        if not migrated_svm:
            print 'SVM with id %s not found.' % svm_id
            abort(404, '404 Not Found - SVM with id %s not found' % svm_id)

        # Restart the VM.
        print 'Unpausing VM...'
        result = migrated_svm.unpause()
        print 'VM running'

        # Save to internal DB.
        migrated_svm.save()

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
    # Returns a list of running svms.
    ############################################################################################################
    @asjson
    def GET_wifiConnect(self):
        ssid = request.params.get('target')
        wifi_manager = wifi.WifiManager()
        wifi_manager.interface = 'wlan0'

        try:
            result = wifi_manager.connect_to_network(ssid)
        except Exception as e:
            msg = 'Error connecting to Wi-Fi network {}: {}'.format(ssid, str(e))
            return ajaxutils.show_and_return_error_dict(msg)

        if result:
            return ajaxutils.JSON_OK
        else:
            return ajaxutils.show_and_return_error_dict('Could not connect to Wi-Fi network {}'.format(ssid))
