class TemplateBase(object):
    '''Base class for templates

    Members:
    _name -- Template name
    '''

    _name = None

    def __init__(self, name):
        self._name = name

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
