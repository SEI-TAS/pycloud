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

"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from routes import Mapper

def make_map(config):
    """Create, configure and return the routes Mapper"""
    mapper = Mapper()
    connect = mapper.connect

    # For backwards compatibility with 0.9.7.
    mapper.explicit = False

    # Note that all of this are relative to the base path, /api.

    if 'pycloud.api.encrypted' in config and config['pycloud.api.encrypted'] == 'true':
        connect('command', '/command', controller='encrypted', action='command')
    else:
        # Service commands.
        connect('list', '/services', controller='services', action='list')
        connect('find', '/services/get', controller='services', action='find')

        # SVM commands.
        connect('startvm', '/servicevm/start', controller='servicevm', action='start')
        connect('stopvm', '/servicevm/stop', controller='servicevm', action='stop')

        # Migration commands.
        connect('/servicevm/migration_svm_metadata', controller='servicevm', action='migration_svm_metadata')
        connect('/servicevm/migration_svm_disk_file', controller='servicevm', action='migration_svm_disk_file')
        connect('/servicevm/abort_migration', controller='servicevm', action='abort_migration')
        connect('/servicevm/migration_generate_credentials', controller='servicevm', action='migration_generate_credentials')
        connect('/servicevm/migration_svm_resume', controller='servicevm', action='migration_svm_resume')

        # Appcommands.
        connect('getAppList', '/apps', controller='apppush', action='getList')
        connect('getApp', '/apps/get', controller='apppush', action='getApp')

        # Metadata commands.
        connect('metadata', '/system', controller='cloudlet', action='metadata')
        connect('get_messages', '/system/get_messages', controller='cloudlet', action='get_messages')

    return mapper
