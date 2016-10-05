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

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.pycloud.pylons.lib.util import asjson
from pycloud.pycloud.model import Service
import tarfile
import json
import os
import shutil
from pylons import request, app_globals


def get_service_json(tar=None):
    member = None
    try:
        member = tar.getmember("service.json")
    except KeyError:
        pass

    f = tar.extractfile(member)
    val = json.loads(f.read())
    f.close()
    return val


class ImportController(BaseController):

    @asjson
    def GET_import(self):
        print "Starting SVM import"
        filename = request.params.get("filename")

        if not filename.endswith(".csvm"):
            print "Invalid file"
            return {"error": "Invalid file"}

        if not os.path.exists(filename):
            print "File does not exist"
            return {"error": "File does not exist"}

        print "Importing file: ", filename

        tar = tarfile.open(filename, "r")
        service = Service(get_service_json(tar))

        svm_cache = app_globals.cloudlet.svmCache
        svm_path = os.path.join(svm_cache, service.service_id)
        disk_image = service.vm_image.disk_image
        state_image = service.vm_image.state_image

        if os.path.exists(svm_path):
            print "Service path already exists"
            return {"error": "Service already exists"}

        os.makedirs(svm_path)
        service.vm_image.disk_image = os.path.join(svm_path, disk_image)
        service.vm_image.state_image = os.path.join(svm_path, state_image)

        try:
            # Extract the disk image to its permanent location.
            tar.extract(disk_image, path=svm_path)

            try:
                # Extract the memory image to its permanent location.
                tar.extract(state_image, path=svm_path)

                # Since usually the memory state from an imported SVM will be incompatible with another computer,
                # refresh the memory state.
                service.refresh_image_memory_state()
            except Exception as e:
                # Create a memory image from a XML template, since the one in the tar was not valid.
                print "Could not load VM XML info; creating new one from disk image and standard XML template."
                service.create_image_memory_state(svm_path)

            service.save()
        except Exception as e:
            print "Exception while importing: " + str(e)
            shutil.rmtree(svm_path)
            return {"error": str(e)}

        print "Done importing!"

        return service
