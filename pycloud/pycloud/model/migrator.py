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
from pycloud.pycloud.model.paired_device_credentials import PairedDeviceDataBundle

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
    if result.status_code != requests.codes.ok:
        raise Exception('Error transferring metadata, code: {}'.format(result.status_code) )
    print 'Metadata was transferred: ' + str(result)

    # We pause the VM before transferring its disk and memory state.
    print 'Pausing VM...'
    result = svm.pause()
    if result == -1:
        raise Exception("Cannot pause VM: %s", str(svm_id))
    print 'VM paused.'

    # Transfer the disk image file.
    print 'Starting disk image file transfer...'
    payload = {'id': svm_id}
    disk_image_full_path = os.path.abspath(svm.vm_image.disk_image)
    files = {'disk_image_file': open(disk_image_full_path, 'rb')}
    result = __send_api_command(remote_host, 'servicevm/migration_svm_disk_file', encrypted, payload, files=files)
    if result.status_code != requests.codes.ok:
        raise Exception('Error transferring disk image file.')
    print 'Disk image file was transferred: ' + str(result)

    # If needed, ask the remote cloudlet for credentials for the devices associated to the SVM.
    if encrypted:
        payload = {'id': svm_id}
        result = __send_api_command(remote_host, 'servicevm/migration_generate_cretendials', encrypted, payload)

    # Do the memory state migration.
    remote_host_name = remote_host.split(':')[0]
    print 'Migrating through libvirt to ' + remote_host_name
    svm.migrate(remote_host_name, p2p=False)
    # TODO: if migration fails, ask remote to remove svm.

    # Notify remote cloudlet that migration finished.
    print 'Telling target cloudlet that migration has finished.'
    payload = {'id': svm_id}
    result = __send_api_command(remote_host, 'servicevm/migration_svm_resume', encrypted, payload)
    if result.status_code != requests.codes.ok:
        raise Exception('Error notifying migration end.')
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
    migrated_svm.fqdn = json_svm['fqdn']

    # Update network data, especially needed in non-bridged mode.
    migrated_svm.update_migrated_network()

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
        return 'no svm'

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
        return 'no backing file'

    # Save to internal DB.
    migrated_svm.save()

    return 'ok'


############################################################################################################
# Generates and returns credentials for the given device.
############################################################################################################
def generate_migration_device_credentials(device_id):
    # Get the device info.
    device = PairedDevice.by_id(device_id)
    if not device:
        raise MigrationException('no device')

    # Get the new credentials for the device on the current deployment.
    deployment = Deployment.get_instance()
    device_keys = deployment.generate_device_credentials(device_id)

    # Bundle the credentials and info needed for a newly paired device.
    device_credentials = PairedDeviceDataBundle()
    device_credentials.ssid = deployment.cloudlet.ssid
    device_credentials.auth_password = device_keys.auth_password
    device_credentials.server_public_key = device_keys.server_private_key
    device_credentials.device_private_key = device_keys.private_key
    device_credentials.load_certificate(deployment.radius_server.cert_file_path)

    return device_credentials


############################################################################################################
# Receives information about a migrated VM.
############################################################################################################
def resume_migrated_svm(svm_id):
    # Find the SVM.
    migrated_svm = ServiceVM.by_id(svm_id)
    if not migrated_svm:
        return False

    # Restart the VM.
    print 'Unpausing VM...'
    result = migrated_svm.unpause()
    print 'VM running'

    # Save to internal DB.
    migrated_svm.save()
