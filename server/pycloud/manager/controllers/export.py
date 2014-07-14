__author__ = 'jdroot'

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.pycloud.model import Service
from pylons import request, g
import os


class ExportController(BaseController):

    def GET_export_svm(self, sid):

        service = Service.by_id(sid)

        path = request.params.get("export_path")
        if not path:
            path = os.path.join(g.cloudlet.export_path, service['_id'] + ".csvm")

        print "Disk Image: ", service.vm_image.disk_image
        print "State Image: ", service.vm_image.state_image

        return "Sid: " + sid + "<br>" + path