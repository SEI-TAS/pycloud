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

import json
import os

# External library for creating HTTP requests.
import requests

from pycloud.pycloud.model import ServiceVM, Service
from pycloud.pycloud.cloudlet import Cloudlet

from pycloud.pycloud.security import encryption
from pycloud.pycloud.model import PairedDevice
from pycloud.pycloud.model.deployment import Deployment
from pycloud.pycloud.model.paired_device_data_bundle import PairedDeviceDataBundle
from pycloud.pycloud.model.message import AddTrustedCloudletDeviceMessage
from pycloud.pycloud.model.servicevm import SVMNotFoundException

################################################################################################################
# Exception type used in this module.
################################################################################################################
class MigrationException(Exception):
    def __init__(self, message):
        super(MigrationException, self).__init__(message)
        self.message = message


############################################################################################################
# Creates the appropriate URL for an API command.
############################################################################################################
def __send_api_command(host, command, encrypted, payload, headers={}, files={}):
    # Set headers.
    if encrypted:
        # TODO: id is only hostname for now. We will evaluate if we want to add hostid to it.
        headers['X-Device-ID'] = Cloudlet.get_hostname()

    if not encrypted:
        remote_url = 'http://{0}/api/{1}'.format(host, command)
    else:
        remote_url = 'http://{0}/api'.format(host)

        # TODO: use proper password to encrypt command.
        password = '' # load_password_from_file()
        encrypted_command = encryption.encrypt_message(command, password)
        payload['command'] = encrypted_command

    print remote_url
    result = requests.post(remote_url, data=payload, headers=headers, files=files)

    if result.status_code != requests.codes.ok:
        raise Exception('Error sending request {}: {} - {}'.format(command, result.status_code, result.text))

    return result


############################################################################################################
# Command to migrate a machine.
############################################################################################################
def migrate_svm(svm_id, remote_host, encrypted):
    # Find the SVM.
    svm = ServiceVM.by_id(svm_id)
    print 'VM found: ' + str(svm)

    # remote_host has host and port.
    print 'Migrating to remote cloudlet: ' + remote_host

    # Transfer the metadata.
    print 'Starting metadata file transfer...'
    payload = json.dumps(svm)
    headers = {'content-type': 'application/json'}
    result = __send_api_command(remote_host, 'servicevm/migration_svm_metadata', encrypted, payload, headers=headers)
    print 'Metadata was transferred: ' + str(result)

    # We pause the VM before transferring its disk and memory state.
    print 'Pausing VM...'
    result = svm.pause()
    if result == -1:
        raise Exception("Cannot pause VM: %s", str(svm_id))
    print 'VM paused.'

    try:
        # Transfer the disk image file.
        print 'Starting disk image file transfer...'
        payload = {'id': svm_id}
        disk_image_full_path = os.path.abspath(svm.vm_image.disk_image)
        files = {'disk_image_file': open(disk_image_full_path, 'rb')}
        result = __send_api_command(remote_host, 'servicevm/migration_svm_disk_file', encrypted, payload, files=files)
        print 'Disk image file was transferred: ' + str(result)

        # If needed, ask the remote cloudlet for credentials for the devices associated to the SVM.
        devices = PairedDevice.by_instance(svm_id)
        for device in devices:
            # TODO: check what an appropriate connection id would be for devices paired through another cloudlet.
            deployment = Deployment.get_instance()
            connection_id = deployment.cloudlet.get_id() + "-" + device.device_id
            payload = {'device_id': device.device_id, 'connection_id': connection_id, 'svm_id': svm_id}
            result = __send_api_command(remote_host, 'servicevm/migration_generate_credentials', encrypted, payload)

            # Store the new credentials so that a device asking for them will get them.
            print result.text
            paired_device_data_bundle = PairedDeviceDataBundle()
            paired_device_data_bundle.fill_from_dict(json.loads(result.text))
            device_command = AddTrustedCloudletDeviceMessage(paired_device_data_bundle)
            device_command.device_id = device.device_id
            device_command.service_id = svm.service_id
            device_command.save()

        # Do the memory state migration.
        remote_host_name = remote_host.split(':')[0]
        print 'Migrating through libvirt to ' + remote_host_name
        svm.migrate(remote_host_name, p2p=False)
    except Exception as e:
        # If migration fails, ask remote to remove svm.
        print 'Error migrating: {}'.format(e.message)
        print 'Requesting migration abort for cleanup...'
        payload = {'svm_id': svm_id}
        result = __send_api_command(remote_host, 'servicevm/abort_migration', encrypted, payload)

        # TODO: re-enabled message cleanup, it was commented out for easier testing.
        devices = PairedDevice.by_instance(svm_id)
        #for device in devices:
        #    AddTrustedCloudletDeviceMessage.clear_messages(device.device_id)

        print 'Migration aborted: ' + str(result)

        # Rethrow exception.
        raise e

    # Notify remote cloudlet that migration finished.
    print 'Telling target cloudlet that migration has finished.'
    payload = {'id': svm_id}
    result = __send_api_command(remote_host, 'servicevm/migration_svm_resume', encrypted, payload)
    print 'Cloudlet notified: ' + str(result)

    # Remove the local VM.
    svm = ServiceVM.by_id(svm_id)
    svm.stop()


############################################################################################################
# Receives information about a migrated VM.
############################################################################################################
def receive_migrated_svm_metadata(svm_json_string):
    # Parse the body of the request as JSON into a python object.
    json_svm = json.loads(svm_json_string)
    if json_svm is None:
        raise MigrationException("No SVM metadata was received")

    # Get information about the SVM.
    print 'Obtaining metadata of SVM to be received.'
    migrated_svm = ServiceVM()
    migrated_svm.fill_from_dict(json_svm)

    # Update network data, especially needed in non-bridged mode.
    migrated_svm.setup_network(update_mac_if_needed=False)

    # Save to internal DB.
    migrated_svm.save()
    print 'SVM metadata stored.'


############################################################################################################
# Receives the disk image file of a migrated SVM.
############################################################################################################
def receive_migrated_svm_disk_file(svm_id, disk_image_object, svm_instances_folder):
    # Get the id and load the metadata for this SVM.
    migrated_svm = ServiceVM.by_id(svm_id)
    if not migrated_svm:
        raise SVMNotFoundException("No SVM found with the given id: {}".format(svm_id))

    # Receive the transferred file and update its path.
    print 'Storing disk image file of SVM in migration.'
    destination_folder = os.path.join(svm_instances_folder, svm_id)
    migrated_svm.vm_image.store(destination_folder, disk_image_object)
    print 'Migrated SVM disk image file stored.'

    # Check that we have the backing file, and rebase the new file so it will point to the correct backing file.
    service = Service.by_id(migrated_svm.service_id)
    if service:
        print 'Rebasing backing file for service %s.' % migrated_svm.service_id
        backing_disk_file = service.vm_image.disk_image
        migrated_svm.vm_image.rebase_disk_image(backing_disk_file)
    else:
        raise MigrationException("No backing file found for service {}".format(migrated_svm.service_id))

    # Save to internal DB.
    migrated_svm.save()


############################################################################################################
# Aborts a migration by removing already created SVM data.
############################################################################################################
def abort_migration(svm_id):
    # Get the id and load the metadata for this SVM.
    migrated_svm = ServiceVM.by_id(svm_id)
    if not migrated_svm:
        raise SVMNotFoundException("No SVM found with the given id {}".format(svm_id))

    print 'Aborting migration, cleaning up...'
    migrated_svm.stop()

    deployment = Deployment.get_instance()
    paired_devices = PairedDevice.by_instance(svm_id)
    for paired_device in paired_devices:
        deployment.unpair_device(paired_device.device_id)
    print 'Cleanup finished.'


############################################################################################################
# Generates and returns credentials for the given device.
############################################################################################################
def generate_migration_device_credentials(device_id, connection_id, svm_id):
    # Get the new credentials for the device on the current deployment.
    print 'Generating credentials for device that will migrate to our cloudlet.'
    device_type = 'mobile'
    deployment = Deployment.get_instance()
    device_keys = deployment.pair_device(device_id, connection_id, device_type)

    # Configure the associated instance.
    paired_device = PairedDevice.by_id(device_id)
    paired_device.instance = svm_id
    paired_device.save()

    # Bundle the credentials and info needed for a newly paired device.
    print 'Bundling credentials for device.'
    device_credentials = PairedDeviceDataBundle()
    device_credentials.cloudlet_name = Cloudlet.get_hostname()
    device_credentials.ssid = deployment.cloudlet.ssid
    device_credentials.auth_password = device_keys.auth_password
    device_credentials.server_public_key = device_keys.server_public_key
    device_credentials.device_private_key = device_keys.private_key
    device_credentials.load_certificate(deployment.radius_server.cert_file_path)

    print 'Returning credentials.'
    return device_credentials.__dict__


############################################################################################################
# Receives information about a migrated VM.
############################################################################################################
def resume_migrated_svm(svm_id):
    # Find the SVM.
    migrated_svm = ServiceVM.by_id(svm_id)
    if not migrated_svm:
        raise SVMNotFoundException("No SVM found with the given id: {}".format(svm_id))

    # Restart the VM, and load network data since it might be in a new network.
    print 'Unpausing VM...'
    migrated_svm.unpause()
    migrated_svm.load_network_data()
    migrated_svm.register_with_dns()
    print 'VM running'

    # Save to internal DB.
    migrated_svm.save()
