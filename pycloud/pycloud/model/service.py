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

from pycloud.pycloud.mongo import Model, ObjectID
from pycloud.pycloud.model.vmimage import VMImage
from pycloud.pycloud.model.servicevm import ServiceVM
import os
import time
from pylons import app_globals

# ###############################################################################################################
# Represents a Service in the system.
################################################################################################################
class Service(Model):
    # Meta class is needed so that minimongo can map this class onto the database.
    class Meta:
        collection = "services"
        external = ['_id', 'service_id', 'description', 'version', 'tags']
        mapping = {
            'vm_image': VMImage
        }

    ################################################################################################################
    # Constructor.
    ################################################################################################################
    def __init__(self, *args, **kwargs):
        self.service_id = None
        self.vm_image = None
        self.description = None
        self.version = None
        self.tags = []
        self.port = None
        self.num_users = None
        self.ideal_memory = None
        self.min_memory = None
        super(Service, self).__init__(*args, **kwargs)
        
    ################################################################################################################
    # Locate a service by its ID
    ################################################################################################################
    # noinspection PyBroadException
    @staticmethod
    def by_internal_id(sid=None):
        rid = sid
        if not isinstance(rid, ObjectID):
            # noinspection PyBroadException
            try:
                rid = ObjectID(rid)
            except:
                return None
        return Service.find_one({'_id': rid})   

    ################################################################################################################
    # Locate a service by its ID
    ################################################################################################################
    # noinspection PyBroadException
    @staticmethod
    def by_id(sid=None):
        try:
            service = Service.find_one({'service_id': sid})
        except:
            return None
        return service

    ################################################################################################################
    # Cleanly and safely gets a Service and removes it from the database
    ################################################################################################################
    @staticmethod
    def find_and_remove(sid):
        # Find the right service and remove it. find_and_modify will only return the document with matching id
        return Service.find_and_modify(query={'service_id': sid}, remove=True)

    ################################################################################################################
    # Returns a new or existing Service VM instance associated to this service.
    ################################################################################################################
    def get_vm_instance(self, join=False, clone_full_image=False):
        service_supports_sharing = (self.num_users > 0)
        print 'Sharing supported: ' + str(service_supports_sharing)
        print 'Share requested: ' + str(join)
        if service_supports_sharing and join:
            # Return the first ServiceVM we find.
            print 'Looking for available SVMs...'
            service_vms = ServiceVM.by_service(self.service_id)
            if len(service_vms) > 0:
                svm = service_vms[0]
                print 'Returning SVM with id {}'.format(svm._id)
                return svm

        # If no ServiceVMs for that ID were found, or service is not shared, or join=False, create a new one.
        print 'No SVM was available or a new instance was requested; starting a new instance.'
        svm = ServiceVM()
        svm.generate_random_id()
        svm.service_id = self.service_id
        svm.service_port = self.port

        # Set up the new SVM's image files based on the service's template.
        new_svm_folder = os.path.join(app_globals.cloudlet.svmInstancesFolder, svm['_id'])
        svm.vm_image = self.vm_image.clone(new_svm_folder, clone_full_image=clone_full_image)

        # Start the SVM.
        try:
            svm.start()
            svm.save()
        except Exception as e:
            svm.stop()
            raise e

        return svm

    ################################################################################################################
    #
    ################################################################################################################
    def create_image_memory_state(self, os_type='Linux'):
        print 'Creating SVM...'
        svm = ServiceVM()
        svm.generate_random_id()
        svm.service_id = self.service_id
        svm.service_port = self.port
        svm.vm_image = self.vm_image

        # Set the OS type.
        if os_type == 'Windows':
            svm.os = "win"
        else:
            svm.os = "lin"

        # Create the VM (this will also start it).
        template_xml_file = os.path.abspath(app_globals.cloudlet.newVmXml)
        svm.create(template_xml_file)
        svm.save()

        # Stop and store the memory image state.
        svm.stop(foce_save_state=True, cleanup_files=False)
        print "VM info and state created from template."

    ####################################################################################################################
    # Attempt to refresh the memory state of the VM Image for this service.
    ####################################################################################################################
    def refresh_image_memory_state(self):
        svm = None
        try:
            # Create an independent new SVM for this service.
            print "Starting service SVM to refresh memory state."
            svm = self.get_vm_instance(join=False, clone_full_image=True)

            # Wait for a bit to allow it to boot up.
            boot_wait_time_in_s = 15
            time.sleep(boot_wait_time_in_s)

            svm.stop(foce_save_state=True, cleanup_files=False)
            print "Service VM stopped, and machine state saved."

            # Permanently store the VM.
            vm_image_folder = os.path.dirname(self.vm_image.disk_image)
            print 'Moving Service VM Image to cache, from folder {} to folder {}.'.format(
                os.path.dirname(svm.vm_image.disk_image), vm_image_folder)
            svm.vm_image.move(vm_image_folder)
            svm.vm_image.protect()
            print 'VM Image updated.'
        except Exception as e:
            if svm:
                svm.stop()

            error_msg = "Exception updating SVM memory state: " + str(e)
            raise Exception(error_msg)

    ################################################################################################################
    # Returns a VM linked to the original VM image so that it can be modified.
    ################################################################################################################
    def get_root_vm(self):
        svm = ServiceVM()
        svm.generate_random_id()
        svm.service_id = self.service_id
        svm.service_port = self.port
        svm.vm_image = self.vm_image
        return svm

    ################################################################################################################
    # Removes this Service and all of its files
    ################################################################################################################
    def destroy(self, force=False):
        # Make sure we are no longer in the database
        Service.find_and_remove(self.service_id)

        # Delete our backing files
        self.vm_image.cleanup(force)

    ################################################################################################################
    # Removes this Service and all of its files
    ################################################################################################################
    def export(self):
        # We manually turn the service in to a dict because @asjson forces external fields only
        import json
        return json.dumps(
            {
                "service_id": self.service_id,
                "vm_image": self.vm_image.export(),
                "description": self.description,
                "version": self.version,
                "tags": [str(tag) for tag in self.tags],
                "port": self.port,
                "num_users": self.num_users,
                "ideal_memory": self.ideal_memory,
                "min_memory": self.min_memory
            }
        )
