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

from collection import MongoCollection


class MetaInfo(object):

    collection = None
    external = None
    mapping = None

    def __init__(self, meta):
        self.__dict__.update(meta.__dict__)


class MetaObject(type):

    def __new__(mcs, name, bases, attrs):
        new_class = super(MetaObject, mcs).__new__(mcs, name, bases, attrs)

        try:
            meta = getattr(new_class, 'Meta')
            delattr(new_class, 'Meta')
        except:
            meta = None

        # Will be none for Model
        if meta is not None:
            info = MetaInfo(meta)
            info.collection = info.collection or name.lower()

            # Create the collection and add it to the new class
            import pycloud.pycloud.cloudlet as cloudlet
            coll = MongoCollection(cloudlet.get_cloudlet_instance().db, info.collection, obj_class=new_class)
            new_class._collection = coll

            # Create the external attributes list and add it to the new class
            if isinstance(info.external, list):
                #print 'Mapping _external attributes for "%s"' % str(new_class)
                #print info.external
                new_class._external = info.external
            else:
                new_class._external = None

            if isinstance(info.mapping, dict):
                new_class.variable_mapping = info.mapping
            else:
                new_class.variable_mapping = None

            # Setup find and find one static methods
            new_class.find = new_class._collection.find
            new_class.find_one = new_class._collection.find_one
            new_class.find_and_modify = new_class._collection.find_and_modify
            new_class.external = external

        return new_class

def external(obj):
    ret = obj
    if hasattr(ret, '_external'):
        if isinstance(ret._external, list):
            ret = {}
            for key in obj._external:
                tmp = obj[key]
                if hasattr(tmp, 'external'):
                    if hasattr(tmp.external, '__call__'):
                        tmp = tmp.external()
                ret[key] = tmp
    return ret