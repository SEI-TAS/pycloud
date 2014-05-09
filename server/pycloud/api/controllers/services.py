import logging

# Pylon imports.
from pylons import request

# Controller to derive from.
from pycloud.pycloud.pylons.lib.base import BaseController

# Repository to look for SVMs, and logging util.
from pycloud.pycloud.pylons.lib.util import asjson
from pycloud.pycloud.utils import timelog

from pycloud.pycloud.model import Service, VMImage

# Used to modify UUID of a saved VM.
from pycloud.pycloud.vm.vmnetx import LibvirtQemuMemoryHeader
from pycloud.pycloud.model.servicevm import ServiceVM

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
        f2 = open('./data/svmcache/edu.cmu.sei.ams.face_rec_service_opencv/face_opencv.qcow2.lqs', 'r+')
        hdr = LibvirtQemuMemoryHeader(f2)
        f = open('basic_header.txt', 'rw+')
        f.write(hdr.xml)
        f.flush()
        f.close()

        xmlDescription = ServiceVM.get_hypervisor().saveImageGetXMLDesc('./data/svmcache/edu.cmu.sei.ams.face_rec_service_opencv/face_opencv.qcow2.lqs', 0)
        f = open('basic_header2.txt', 'rw+')
        f.write(xmlDescription)
        f.flush()
        f.close()

        # service = Service.by_id('edu.cmu.sei.ams.face_rec_service_opencv')
        # svm = service.get_vm_instance()
        return 'ok'