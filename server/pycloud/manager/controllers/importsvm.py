__author__ = 'jdroot'

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.pycloud.pylons.lib.util import asjson
from pycloud.pycloud.model import Service
import tarfile
import json
import os
from pylons import request, g


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
            return {"error": "Invalid file"}
        if not os.path.exists(filename):
            return {"error": "File does not exist"}

        print "Importing file: ", filename

        tar = tarfile.open(filename, "r")
        service = Service(get_service_json(tar))

        svm_cache = g.cloudlet.svmCache
        svm_path = os.path.join(svm_cache, service.service_id)
        disk_image = service.vm_image.disk_image
        state_image = service.vm_image.state_image

        if os.path.exists(svm_path):
            return {"error": "Service already exists"}

        os.makedirs(svm_path)

        tar.extract(disk_image, path=svm_path)
        tar.extract(state_image, path=svm_path)

        service.vm_image.disk_image = os.path.join(svm_path, disk_image)
        service.vm_image.state_image = os.path.join(svm_path, state_image)

        service.save()

        print "Done importing!"

        return service