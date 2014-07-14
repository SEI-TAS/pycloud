__author__ = 'jdroot'

from pycloud.pycloud.pylons.lib.base import BaseController
from pylons import request, g


class ExportController(BaseController):

    def GET_export_svm(self, sid):
        path = request.params.get("export_path")
        if not path:
            path = g.cloudlet.export_path + sid + ".csvm"
        return "Sid: " + sid + "\n" + path