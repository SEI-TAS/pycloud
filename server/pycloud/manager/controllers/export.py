__author__ = 'jdroot'

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.pycloud.pylons.lib.util import asjson
from pycloud.pycloud.model import Service
from pylons import request, g
import os
import tarfile
import StringIO


class ExportController(BaseController):

    @asjson
    def GET_export_svm(self, sid):
        service = Service.by_id(sid)

        if not service:
            return "Service Not Found"

        path = request.params.get("export_path")
        if not path:
            path = os.path.join(g.cloudlet.export_path, service.service_id + ".csvm")

        print "Disk Image: ", service.vm_image.disk_image
        print "State Image: ", service.vm_image.state_image

        tar = tarfile.open(path, "w:gz")
        tar.add(service.vm_image.disk_image)
        tar.add(service.vm_image.state_image)
        add_string_to_tar(data=service.export(), filename=service.service_id + ".json", tar=tar)
        tar.close()

        return path


def add_string_to_tar(data=None, filename=None, tar=None):
    if not data or not filename or not tar:
        return
    sio = StringIO.StringIO()
    sio.write(data)
    sio.seek(0)

    tarinfo = tarfile.TarInfo(name=filename)
    tarinfo.size = len(sio.buf)
    tar.addfile(tarinfo=tarinfo, fileobj=sio)