__author__ = 'jdroot'

from pylons import config
from mako.exceptions import TemplateLookupException
from mako import exceptions


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
