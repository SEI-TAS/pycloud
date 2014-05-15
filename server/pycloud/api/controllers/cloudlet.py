__author__ = 'jdroot'

from pycloud.pycloud.pylons.lib.base import BaseController
from pylons import request
from pycloud.pycloud.pylons.lib.util import asjson
from pycloud.pycloud.utils import timelog
from pycloud.pycloud.cloudlet import Cloudlet
from pycloud.pycloud.model import Service

class CloudletController(BaseController):

    @asjson
    def GET_metadata(self):
        timelog.TimeLog.reset()
        timelog.TimeLog.stamp("Request received: get metadata.")
        ret = Cloudlet.system_information()
        ret.services = Service.find()
        timelog.TimeLog.stamp("Sending response back to " + request.environ['REMOTE_ADDR'])
        return ret