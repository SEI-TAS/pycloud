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
import os

################################################################################################################
# Represents a Cloudlet-Ready app stored in the system.
################################################################################################################
class App(Model):
    # Meta class is needed so that minimongo can map this class onto the database.
    class Meta:
        collection = "apps"
        external = ['_id', 'name', 'service_id', 'description', 'package_name',
                    'min_android_version', 'md5sum', 'app_version', 'tags']
        mapping = {

        }

    ################################################################################################################
    # Constructor.
    ################################################################################################################
    def __init__(self, *args, **kwargs):
        # self._id = None  # Commented out make Mongo auto populate it
        self.name = None
        self.service_id = None
        self.description = None
        self.package_name = None
        self.min_android_version = None
        self.md5sum = None
        self.app_version = None
        self.tags = None
        self.apk_file = None
        super(App, self).__init__(*args, **kwargs)

    ################################################################################################################
    # Locate an App by its ID
    ################################################################################################################
    @staticmethod
    def by_id(oid=None):
        rid = oid
        if not isinstance(rid, ObjectID):
            # noinspection PyBroadException
            try:
                rid = ObjectID(rid)
            except:
                return None
        return App.find_one({'_id': rid})

    ################################################################################################################
    # Get the filename given a full path.
    ################################################################################################################
    def file_name(self):
        return os.path.basename(self.apk_file)
    
    ################################################################################################################
    # Cleanly and safely gets a App and removes it from the database
    ################################################################################################################
    @staticmethod
    def find_and_remove(sid):
        # Find the right app and remove it. find_and_modify will only return the document with matching id.
        return App.find_and_modify(query={'_id': sid}, remove=True)    
