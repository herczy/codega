'''Handling templates and template sets.

A template is an object that - given the proper bindings - can create some kind of output. A template
set on the other hand is a collection of templates. All templates are accessed through a template set.

This module also contains MakoTemplateset which loads mako templates. Further templates can be
supported if needed.
'''
from UserDict import DictMixin

from error import TemplateNotFoundError
from stringio import StringIO

class TemplateBase(object):
    '''Base class for templates'''

    _name = None

    def render(self, bindings):
        '''Render the template with the given bindings'''

        raise NotImplementedError("TemplateBase.render is abstract")

class TemplatesetBase(object):
    '''Template set base class'''

    def __init__(self):
        pass

    def get_template(self, name):
        '''Get the template object from the given name

        Arguments:
        name -- Name of the template to find
        '''

        raise NotImplementedError("TemplatesetBase.locate_template is abstract")

    def render(self, name, bindings):
        '''Renders a template located by its by name

        Arguments:
        name -- Name of the template to find
        bindings -- Bindings to pass to the template renderer
        '''

        return self.get_template(name).render(bindings)
