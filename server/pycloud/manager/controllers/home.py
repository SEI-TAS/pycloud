import logging

from pylons import request, response, session, tmpl_context as c, url
from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.manager.lib.pages import HomePage

from pycloud.pycloud.cloudlet import Cloudlet
from pycloud.pycloud.pylons.lib.util import asjson

log = logging.getLogger(__name__)

################################################################################################################
# Controller for the main page.
################################################################################################################
class HomeController(BaseController):

    ############################################################################################################
    # Shows the main page.  
    ############################################################################################################
    def GET_index(self):
        # Mark the active tab.
        c.home_active = 'active'

        # Get current metadata.
        page = HomePage()
        ret = Cloudlet.system_information()
        page.machine_status = ret

        # Render the page with the grid.
        return page.render()

    @asjson
    def GET_state(self):
        machine_state = Cloudlet.system_information()
        return machine_state
