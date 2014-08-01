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
        filename = request.params.get("filename")

        if not filename.endswith(".csvm"):
            return {"error": "Invalid file"}

        tar = tarfile.open(filename, "r")
        service = Service(get_service_json(tar))

        svm_cache = g.cloudlet.svmCache
        svm_path = os.path.join(svm_cache, service.service_id) + "2"

        if os.path.exists(svm_path):
            return {"error": "Service already exists"}

        os.makedirs(svm_path)

        tar.extract(service.vm_image.disk_image, path=svm_path)
        tar.extract(service.vm_image.state_image, path=svm_path)

        print svm_path


        return service