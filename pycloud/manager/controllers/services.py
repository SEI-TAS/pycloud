import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from pycloud.manager.lib.base import BaseController

from webhelpers.html.grid import Grid

from pycloud.pycloud.servicevm import svmrepository

from pycloud.manager.lib.pages import ServicesPage

log = logging.getLogger(__name__)

class ServicesController(BaseController):

    def GET_index(self):
        # Get a list of existing stored VMs in the cache.
        serviceVmRepo = svmrepository.ServiceVMRepository()
        vmList = serviceVmRepo.getStoredServiceVMList()

        # Create an item list with the info to display.
        itemList = []
    	for storedVMId in vmList:
            storedVM = vmList[storedVMId]
            newItem = {'service_id':storedVM.metadata.serviceId,
                       'name':storedVM.name,
                       'service_port':storedVM.metadata.servicePort,
                       'folder':storedVM.folder}
            itemList.append(newItem)

    	c.myGrid = Grid(itemList, ['service_id', 'name', 'service_port', 'folder'])
        return ServicesPage().render()

