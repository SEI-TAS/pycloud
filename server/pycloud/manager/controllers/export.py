__author__ = 'jdroot'

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.pycloud.model import Service
from pylons import request, g
import os
import zipfile


class ExportController(BaseController):

    def GET_export_svm(self, sid):

        service = Service.by_id(sid)

        if not service:
            return "Service Not Found"

        path = request.params.get("export_path")
        if not path:
            path = os.path.join(g.cloudlet.export_path, service['_id'] + ".csvm")

        print "Disk Image: ", service.vm_image.disk_image
        print "State Image: ", service.vm_image.state_image

        zipf = zipfile.ZipFile(path, "w", allowZip64=True)  # Needed for files larger than 2gb
        zipf.write(service.vm_image.disk_image)
        zipf.write(service.vm_image.state_image)
        zipf.close()

        return "Ok"