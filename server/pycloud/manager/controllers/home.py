import logging

from pylons import request, response, session, tmpl_context as c, url
from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.manager.lib.pages import HomePage

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

        # Render the page with the grid.
        return HomePage().render()
