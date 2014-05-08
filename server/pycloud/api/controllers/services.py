import logging

# Pylon imports.
from pylons import request

# Controller to derive from.
from pycloud.pycloud.pylons.lib.base import BaseController

# Repository to look for SVMs, and logging util.
from pycloud.pycloud.pylons.lib.util import asjson
from pycloud.pycloud.utils import timelog

from pycloud.pycloud.model import Service, VMImage

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
        serviceId = request.GET['serviceId']
        print '\n*************************************************************************************************'
        timelog.TimeLog.reset()
        timelog.TimeLog.stamp("Request received: find cached Service VM.")
        ret = Service.by_id(serviceId)
        if not ret:
            ret = {}
        # Send the response.
        timelog.TimeLog.stamp("Sending response back to " + request.environ['REMOTE_ADDR'])
        return ret

    @asjson
    def GET_test(self):

        service = Service()
        service._id = 'edu.cmu.sei.ams.face_rec_service_opencv'
        service.description = 'test'
        service.num_users = 0
        service.vm_image = VMImage()

        service.vm_image.disk_image = 'edu.cmu.sei.ams.face_rec_service_opencv/face_opencv.qcow2'
        service.vm_image.state_image = 'edu.cmu.sei.ams.face_rec_service_opencv/face_opencv.qcow2.lqs'
        service.tags = ['a', 'b', 'c']
        service.port = 1234

        service.save()

        return {}