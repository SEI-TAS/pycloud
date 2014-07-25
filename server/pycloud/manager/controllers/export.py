__author__ = 'jdroot'

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.pycloud.pylons.lib.util import asjson2
from pycloud.pycloud.model import Service
from pylons import request, g
import os


class ExportController(BaseController):

    @asjson2
    def GET_export_svm(self, sid):

        service = Service.by_id(sid)

        if not service:
            return "Service Not Found"

        path = request.params.get("export_path")
        if not path:
            path = os.path.join(g.cloudlet.export_path, service.service_id + ".csvm")

        print "Disk Image: ", service.vm_image.disk_image
        print "State Image: ", service.vm_image.state_image



        # tarf = tarfile.open(path, "w:gz")
        # tarf.add(service.vm_image.disk_image)
        # tarf.add(service.vm_image.state_image)
        # tarf.close()

        return "this text should come out"