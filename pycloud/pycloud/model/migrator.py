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
from pycloud.pycloud.cloudlet import Cloudlet, get_cloudlet_instance

from pycloud.pycloud.security import encryption
from pycloud.pycloud.model import PairedDevice
from pycloud.pycloud.model.deployment import Deployment
from pycloud.pycloud.model.paired_device_data_bundle import PairedDeviceDataBundle
from pycloud.pycloud.model.message import AddTrustedCloudletDeviceMessage, ConnectToNewCloudletMessage
from pycloud.pycloud.model.servicevm import SVMNotFoundException
from pycloud.pycloud.model.cloudlet_credential import CloudletCredential
from pycloud.pycloud.model.deployment import DeviceAlreadyPairedException

# API migration commands
MIGRATE_METADATA_CMD = '/servicevm/migration_svm_metadata'
MIGRATE_DISK_CMD = '/servicevm/migration_svm_disk_file'
MIGRATE_CREDENTIALS_CMD = '/servicevm/migration_generate_credentials'
MIGRATE_RESUME_CMD = '/servicevm/migration_svm_resume'
MIGRATE_ABORT_CMD = '/servicevm/abort_migration'


################################################################################################################
# Exception type used in this module.
################################################################################################################
class MigrationException(Exception):
    def __init__(self, message):
        super(MigrationException, self).__init__(message)
        self.message = message


############################################################################################################
#
############################################################################################################
def __print_request(prepared):
    print('{}\n{}\n{}\n\n{}'.format(
        '-----------START-----------',
        prepared.method + ' ' + prepared.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in prepared.headers.items()),
        prepared.body,
    ))


############################################################################################################
# Creates the appropriate URL for an API command.
############################################################################################################
def __send_api_command(host, command, encrypted, payload, headers={}, files={}):
    if encrypted:
        # We need to send our id so that the remote API will be able to decrypt our requests properly.
        headers['X-Device-ID'] = Cloudlet.get_id()

    if not encrypted:
        remote_url = 'http://{0}/api/{1}'.format(host, command)
    else:
        remote_url = 'http://{0}/api/command'.format(host)

        # Get the appropriate encryption password for this host.
        cloudlet_fqdn = host.split(':')[0]
        credentials = CloudletCredential.by_cloudlet_fqdn(cloudlet_fqdn)
        if not credentials:
            raise Exception('Credentials to encrypt communication to cloudlet with fqdn {} are not stored in the DB'.format(cloudlet_fqdn))

        # Add all payload elements.
        command_string = command
        for param in payload:
            command_string += "&" + param + "=" + str(payload[param])

        # Encrypt the command and add it as a param.
        encrypted_command = encryption.encrypt_message(command_string, credentials.encryption_password)
        payload = {}
        payload['command'] = encrypted_command

    req = requests.Request('POST', remote_url, data=payload, headers=headers, files=files)
    prepared = req.prepare()
    print remote_url

    session = requests.Session()
    response = session.send(prepared)

    if response.status_code != requests.codes.ok:
        raise Exception('Error sending request {}: {} - {}'.format(command, response.status_code, response.text))

    response_text = response.text
    if encrypted and response.text and response.text != '':
        response_text = encryption.decrypt_message(response.text, credentials.encryption_password)

    return response, response_text


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
    payload = {'svm_json_string': svm.to_json_string()}
    result, response_text = __send_api_command(remote_host, MIGRATE_METADATA_CMD, encrypted, payload)
    print 'Metadata was transferred: ' + str(result)

    # We pause the VM before transferring its disk and memory state.
    print 'Pausing VM...'
    was_pause_successful = svm.pause()
    if not was_pause_successful:
        raise Exception("Cannot pause VM: %s", str(svm_id))
    print 'VM paused.'

    try:
        # Transfer the disk image file.
        print 'Starting disk image file transfer...'
        payload = {'id': svm_id}
        disk_image_full_path = os.path.abspath(svm.vm_image.disk_image)
        files = {'disk_image_file': open(disk_image_full_path, 'rb')}
        result, response_text = __send_api_command(remote_host, MIGRATE_DISK_CMD, encrypted, payload, files=files)
        print 'Disk image file was transferred: ' + str(result)

        # Do the memory state migration.
        remote_host_name = remote_host.split(':')[0]
        print 'Migrating through libvirtd to ' + remote_host_name
        svm.migrate(remote_host_name)
        print 'Memory migration through libvirtd completed'

        # If needed, ask the remote cloudlet for credentials for the devices associated to the SVM.
        devices = PairedDevice.by_instance(svm_id)
        for device in devices:
            # So that the paired device has a connection id on the remote cloudlet, we set it as this cloudlet's id
            # plus the device id. Connection id is commonly used with USB or Bluetooth pairing as a way to identify
            # the ID of the physical connection used when pairing. This gives similar auditing possibilities.
            print 'Starting remote credentials generation for device {}...'.format(device.device_id)
            deployment = Deployment.get_instance()
            connection_id = deployment.cloudlet.get_id() + "-" + device.device_id
            payload = {'device_id': device.device_id, 'connection_id': connection_id, 'svm_id': svm_id}
            response, serialized_credentials = __send_api_command(remote_host, MIGRATE_CREDENTIALS_CMD, encrypted, payload)
            print 'Remote credentials were generated: ' + str(response)

            # De-serializing generated data.
            print serialized_credentials
            paired_device_data_bundle = PairedDeviceDataBundle()
            paired_device_data_bundle.fill_from_dict(json.loads(serialized_credentials))

            # Create the appropriate command.
            data_contains_only_cloudlet_info = paired_device_data_bundle.auth_password is None
            if data_contains_only_cloudlet_info:
                device_command = ConnectToNewCloudletMessage(paired_device_data_bundle)
            else:
                device_command = AddTrustedCloudletDeviceMessage(paired_device_data_bundle)

            # Add device and service id data, and store the message to be picked up by the phone.
            device_command.device_id = device.device_id
            device_command.service_id = svm.service_id
            device_command.save()
    except Exception as e:
        # If migration fails, ask remote to remove svm.
        print 'Error migrating: {}'.format(e.message)
        print 'Requesting migration abort for cleanup...'
        payload = {'svm_id': svm_id}
        result, response_text = __send_api_command(remote_host, MIGRATE_ABORT_CMD, encrypted, payload)

        # Remove pending migration messages.
        devices = PairedDevice.by_instance(svm_id)
        for device in devices:
            AddTrustedCloudletDeviceMessage.clear_messages(device.device_id)

        print 'Migration aborted: ' + str(result)
        raise e

    # Notify remote cloudlet that migration finished.
    print 'Asking remote cloudlet to resume migrated VM.'
    payload = {'id': svm_id}
    result, response_text = __send_api_command(remote_host, MIGRATE_RESUME_CMD, encrypted, payload)
    print 'Cloudlet notified: ' + str(result)

    # Remove the local VM.
    svm = ServiceVM.by_id(svm_id)
    svm.stop()


############################################################################################################
# Receives information about a migrated VM.
############################################################################################################
def receive_migrated_svm_metadata(svm_json_string):
    # Parse the body of the request as JSON into a python object.
    json_svm_dict = json.loads(svm_json_string)
    if json_svm_dict is None:
        raise MigrationException("No SVM metadata was received")

    # Get information about the SVM.
    print 'Obtaining metadata of SVM to be received (json string: {}).'.format(svm_json_string)
    migrated_svm = ServiceVM()
    migrated_svm.fill_from_dict(json_svm_dict)
    migrated_svm.ready = False

    # Update network data, especially needed in non-bridged mode.
    migrated_svm.setup_network(update_mac_if_needed=False)

    # Save to internal DB.
    migrated_svm.save()
    print 'SVM metadata stored for SVM with id {}'.format(migrated_svm._id)


############################################################################################################
# Receives the disk image file of a migrated SVM.
############################################################################################################
def receive_migrated_svm_disk_file(svm_id, disk_image_object, svm_instances_folder):
    # Get the id and load the metadata for this SVM.
    migrated_svm = ServiceVM.by_id(svm_id, only_find_ready_ones=False)
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
    migrated_svm = ServiceVM.by_id(svm_id, only_find_ready_ones=False)
    if not migrated_svm:
        raise SVMNotFoundException("No SVM found with the given id {}".format(svm_id))

    print 'Aborting migration, cleaning up...'
    migrated_svm.stop()

    # Unpairing all paired devices that were using this VM.
    deployment = Deployment.get_instance()
    paired_devices = PairedDevice.by_instance(svm_id)
    for paired_device in paired_devices:
        deployment.unpair_device(paired_device.device_id)
    print 'Cleanup finished.'


############################################################################################################
# Generates and returns credentials for the given device.
############################################################################################################
def generate_migration_device_credentials(device_id, connection_id, svm_id):
    print 'Preparing credentials and cloudlet information.'
    device_credentials = PairedDeviceDataBundle()
    try:
        # Get the new credentials for the device on the current deployment.
        print 'Generating credentials for device that will migrate to our cloudlet.'
        deployment = Deployment.get_instance()
        device_type = 'mobile'
        device_keys = deployment.pair_device(device_id, connection_id, device_type)

        # Configure the associated instance.
        paired_device = PairedDevice.by_id(device_id)
        paired_device.instance = svm_id
        paired_device.save()

        # Bundle the credentials for a newly paired device.
        print 'Bundling credentials for device.'
        device_credentials.auth_password = device_keys.auth_password
        device_credentials.server_public_key = device_keys.server_public_key
        device_credentials.device_private_key = device_keys.private_key
        device_credentials.load_certificate(deployment.radius_server.cert_file_path)
    except DeviceAlreadyPairedException as e:
        print 'Credentials not generated: ' + e.message

    # Bundle common cloudlet information.
    print 'Bundling cloudlet information for device.'
    cloudlet = get_cloudlet_instance()
    device_credentials.cloudlet_name = Cloudlet.get_hostname()
    device_credentials.cloudlet_fqdn = Cloudlet.get_fqdn()
    device_credentials.cloudlet_port = 9999                 # TODO: find a way to get the port we (API) are listening to
    device_credentials.cloudlet_encryption_enabled = cloudlet.api_encrypted
    device_credentials.ssid = cloudlet.ssid

    print 'Returning credentials and cloudlet data.'
    return device_credentials.__dict__


############################################################################################################
# Receives information about a migrated VM.
############################################################################################################
def resume_migrated_svm(svm_id):
    # Find the SVM.
    migrated_svm = ServiceVM.by_id(svm_id, only_find_ready_ones=False)
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
