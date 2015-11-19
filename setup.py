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

from setuptools import setup, find_packages

from pip.req import parse_requirements
from pip.download import PipSession

# Parse the requirements file.
pip_session = PipSession()
reqs = [str(ir.req) for ir in parse_requirements('requirements.txt', session=pip_session)]

setup(
    name='pycloud',
    version='0.4.0',
    description='Cloudlet Server',
    author='Software Engineering Institute',
    author_email='Sebastian Echeverria <secheverria@sei.cmu.edu>',
    url='',
    install_requires=reqs,
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    package_data={
        'templates': ['pycloud/manager/templates/*'],
        'public': ['pycloud/manager/public/**.*'],
        'xml': ['*.xml']
    },
    entry_points="""
    [console_scripts]
    pycloud-api=pycloud:start_api
    pycloud-manager=pycloud:start_manager

    [paste.app_factory]
    api = pycloud.api:make_app
    manager = pycloud.manager:make_app

    [paste.app_install]
    api = pylons.util:PylonsInstaller
    manager = pylons.util:PylonsInstaller
    """
)
