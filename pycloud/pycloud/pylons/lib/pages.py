from pylons import config

class Templated(object):

    def template(self):
        from pycloud.pycloud.pylons.config.templates import tm
        return tm.get(self.__class__.__name__)

    def render(self):
        template = self.template()
        if template:
            res = template.render(page=self)
            return res
        return "not found"


class BasePage(Templated):

    def __init__(self, title="Cloudlet"):
        self.title = title
        self.form_values = {}
        self.form_errors = {}
