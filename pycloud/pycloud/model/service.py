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
        print 'No SVM was available, starting a new instance.'
        svm = ServiceVM()
        svm.generate_random_id()
        svm.service_id = self.service_id
        svm.service_port = self.port

        # Set up the new SVM's image files based on the service's template.
        new_svm_folder = os.path.join(app_globals.cloudlet.svmInstancesFolder, svm['_id'])
        svm.vm_image = self.vm_image.clone(new_svm_folder, clone_full_image=clone_full_image)

        # Start the SVM.
        svm.start()
        svm.save()
        return svm

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
