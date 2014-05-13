import logging

# Pylon imports.
from pylons import request
from pylons.controllers.util import abort

# Controller to derive from.
from pycloud.pycloud.pylons.lib.base import BaseController

# Repository to look for SVMs, and logging util.
from pycloud.pycloud.pylons.lib.util import asjson
from pycloud.pycloud.utils import timelog

from pycloud.pycloud.model import Service, App

log = logging.getLogger(__name__)


################################################################################################################
# Class that handles Service related HTTP requests to a Cloudlet.
################################################################################################################
class ServicesController(BaseController):
            
    ################################################################################################################
    # Get a list of the services in the VM. In realiy, for now at least, it actually get a list of services that
    # have associated ServiceVMs in the cache.
    ################################################################################################################
    @asjson
    def GET_list(self):
        print '\n*************************************************************************************************'
        timelog.TimeLog.reset()
        timelog.TimeLog.stamp("Request received: get list of Services.")

        services = Service.find()
        
        # Send the response.
        timelog.TimeLog.stamp("Sending response back to " + request.environ['REMOTE_ADDR'])
        return services
            
    ################################################################################################################
    # Called to check if a specific service is already provided by a cached Service VM on this server.
    ################################################################################################################
    @asjson
    def GET_find(self):
        # Look for the VM in the repository.
        sid = request.GET['serviceId']
        print '\n*************************************************************************************************'
        timelog.TimeLog.reset()
        timelog.TimeLog.stamp("Request received: find cached Service VM.")
        ret = Service.by_id(sid)
        if not ret:
            abort(404, '404 Not Found - service for %s not found' % sid)
        else:
            # Send the response.
            timelog.TimeLog.stamp("Sending response back to " + request.environ['REMOTE_ADDR'])
            return ret

    @asjson
    def GET_test(self):
        app = App()
        app.name = 'face'
        app.description = 'performs face recognition'
        app.package_name = 'edu.cmu.sei.rtss.cloudlet.facerec'
        app.service_id = 'edu.cmu.sei.ams.face_rec_service'
        app.md5sum = '1325ed86fd781efa6761169600fdae21'
        app.app_version = ''
        app.min_android_version = '9'
        app.tags = ['face', 'c++']
        app.apk_file = './data/apks/face/FaceRecognitionAndroidClient.apk'
        return app