__author__ = 'jdroot'

from pylons import config
from mako.exceptions import TemplateLookupException
from mako import exceptions

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

class TemplateManager():

    def __init__(self):
        self.templates = {}

    def get(self, name, style='html'):
        key = "%s.%s" % (name.lower(), style)
        template = self.templates.get(key)
        if not template:
            try:
                template = config['pylons.g'].mako_lookup.get_template(key)
                if template:
                    self.templates[key] = template
            except TemplateLookupException:
                print exceptions.html_error_template().render()
        if not template:
            raise AttributeError('template for %s not found' % name)
        return template
