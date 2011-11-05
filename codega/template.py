'''Handling templates and template sets.

A template is an object that - given the proper bindings - can create some kind of output. A template
set on the other hand is a collection of templates. All templates are accessed through a template set.

This module also contains MakoTemplateset which loads mako templates. Further templates can be
supported if needed.
'''

from decorators import abstract

from generator.template import TemplateGenerator

class TemplateBase(object):
    '''Base class for templates'''

    _name = None

    @abstract
    def render(self, bindings):
        '''Render the template with the given bindings'''

class TemplatesetBase(object):
    '''Template set base class'''

    def __init__(self):
        pass

    @abstract
    def get_template(self, name):
        '''Get the template object from the given name

        Arguments:
        name -- Name of the template to find
        '''

    def render(self, name, bindings):
        '''Renders a template located by its by name

        Arguments:
        name -- Name of the template to find
        bindings -- Bindings to pass to the template renderer
        '''

        return self.get_template(name).render(bindings)

class TemplatesetGeneratorFactory(object):
    '''
    A factory to create TemplateGenerators based on the provided template set
    and a template name.
    '''

    _template_set = None
    _template_generator = None

    def __init__(self, template_set, template_generator = TemplateGenerator):
        self._template_set = template_set
        self._template_generator = template_generator

    def factory(self, name):
        '''
        Factory to use with the generator decorator.
        '''

        def __factory(func):
            template = self._template_set.get_template(name)
            return self._template_generator(template, func)

        return __factory
