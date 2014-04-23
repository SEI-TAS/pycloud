__author__ = 'jdroot'

from pycloud.pycloud.pylons.lib.base import BaseController
from pylons import g, request
from pycloud.pycloud.pylons.lib.util import asjson
from pycloud.pycloud.utils import timelog

class CloudletController(BaseController):

    @asjson
    def GET_metadata(self):
        timelog.TimeLog.reset()
        timelog.TimeLog.stamp("Request received: get metadata.")
        ret = g.cloudlet.system_information()
        timelog.TimeLog.stamp("Sending response back to " + request.environ['REMOTE_ADDR'])
        return ret