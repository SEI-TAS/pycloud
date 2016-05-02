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

from pycloud.pycloud.mongo import Model, ObjectID


# ###############################################################################################################
# Represents a device authorized into the system.
################################################################################################################
class CloudletCredential(Model):
    # Meta class is needed so that minimongo can map this class onto the database.
    class Meta:
        collection = "cloudlet_credentials"
        external = ['_id', 'cloudlet_id', 'encryption_password']
        mapping = {
        }

    ################################################################################################################
    # Constructor.
    ################################################################################################################
    def __init__(self, *args, **kwargs):
        self.cloudlet_id = None
        self.encryption_password = None
        super(CloudletCredential, self).__init__(*args, **kwargs)

    ################################################################################################################
    # Locate a device by its internal DB ID
    ################################################################################################################
    # noinspection PyBroadException
    @staticmethod
    def by_id(internal_id):
        rid = internal_id
        if not isinstance(rid, ObjectID):
            # noinspection PyBroadException
            try:
                rid = ObjectID(rid)
            except:
                return None
        return CloudletCredential.find_one({'_id': rid})

    ################################################################################################################
    # Locate cloudlet credentials by the id of the cloudlet
    ################################################################################################################
    # noinspection PyBroadException
    @staticmethod
    def by_cloudlet_id(cloudlet_id):
        try:
            credential = CloudletCredential.find_one({'cloudlet_id': cloudlet_id})
        except:
            return None
        return credential
