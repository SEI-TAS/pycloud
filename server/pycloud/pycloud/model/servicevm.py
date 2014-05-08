__author__ = 'jdroot'

from pycloud.pycloud.mongo import Model
from pycloud.pycloud.vm.runningvm import RunningVM


class ServiceVM(Model, RunningVM):
    class Meta:
        collection = "service_vms"

    def __init__(self):
        RunningVM.__init__(self)
        print 'ServiceVM init'

