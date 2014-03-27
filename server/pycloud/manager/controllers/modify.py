import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.templating import render_mako as render

from pycloud.pycloud.pylons.lib.base import BaseController
from pycloud.manager.lib.pages import ModifyPage

log = logging.getLogger(__name__)


################################################################################################################
# Controller for the Modify page.
################################################################################################################
class ModifyController(BaseController):

    def GET_index(self):
        # Mark the active tab.
        c.services_active = 'active'

        # Render the page with the grid.
        return ModifyPage().render()

    def POST_index(self):
        print request.params.get("name")
        return ModifyPage().render()