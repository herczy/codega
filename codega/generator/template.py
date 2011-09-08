'''
Template generators use a function to get template bindings (a dictionary)
and render a template with them.
'''

from base import GeneratorBase

class TemplateGenerator(GeneratorBase):
    '''Generates output with a template.

    Members:
    _template -- Template class
    _bindings -- Function generating bindings
    '''

    _template = None
    _bindings = None

    def __init__(self, template, bindings):
        super(TemplateGenerator, self).__init__()

        self._template = template
        self._bindings = bindings

    def generate(self, source, context):
        return self._template.render(self._bindings(source, context))

    @classmethod
    def factory(cls, template):
        '''Create a factory for template generator'''

        def __factory(func):
            return cls(template, func)

        return __factory
