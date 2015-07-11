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

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.pycloud.pylons.lib.util import asjson
from pycloud.pycloud.model import Service
from pylons import request, app_globals
import os
import tarfile
import StringIO
import time

current_milli_time = lambda: int(round(time.time() * 1000))


class ExportController(BaseController):

    @asjson
    def GET_export_svm(self, sid):
        service = Service.by_id(sid)

        if not service:
            return "Service Not Found"

        path = request.params.get("export_path")
        if not path:
            path = os.path.join(app_globals.cloudlet.export_path, service.service_id + ".csvm")

        print "Disk Image: ", service.vm_image.disk_image
        print "State Image: ", service.vm_image.state_image

        print "Starting export to: ", path
        tar = tarfile.open(path, "w:gz")
        add_file_to_tar(filepath=service.vm_image.disk_image, tar=tar)
        add_file_to_tar(filepath=service.vm_image.state_image, tar=tar)
        add_string_to_tar(data=service.export(), filename="service.json", tar=tar)
        tar.close()

        print "Export complete"

        return path


def add_file_to_tar(filepath=None, tar=None):
    name = os.path.basename(filepath)
    tar.add(filepath, arcname=name)


def add_string_to_tar(data=None, filename=None, tar=None):
    if not data or not filename or not tar:
        return
    sio = StringIO.StringIO()
    sio.write(data)
    sio.seek(0)

    tarinfo = tarfile.TarInfo(name=filename)
    tarinfo.size = len(sio.buf)
    tarinfo.mtime = time.time()
    tar.addfile(tarinfo=tarinfo, fileobj=sio)