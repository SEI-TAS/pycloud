import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons import g

from pycloud.pycloud.pylons.lib.base import BaseController

from webhelpers.html.grid import Grid

from pycloud.pycloud.servicevm import svmrepository

from pycloud.manager.lib.pages import ServiceVMsPage

log = logging.getLogger(__name__)

class ServiceVMsController(BaseController):

    def GET_index(self):
        # Get a list of running ServiceVM instances.
        instanceManager = g.cloudlet.instanceManager
        instanceList = instanceManager.getServiceVMInstances()

        # Create an item list with the info to display.
        itemList = []
    	for serviceVMInstanceId in instanceList:
            serviceVMInstance = instanceList[serviceVMInstanceId]
            newItem = {'instance_id':serviceVMInstance.instanceId,
                       'service_id':serviceVMInstance.serviceId,
                       'service_port':serviceVMInstance.serviceHostPort,
                       'ssh_port':serviceVMInstance.sshHostPort,                       
                       'folder':serviceVMInstance.getInstanceFolder()}
            itemList.append(newItem)

    	c.myGrid = Grid(itemList, ['instance_id', 'service_id', 'service_port', 'ssh_port', 'folder'])
        return ServiceVMsPage().render()

