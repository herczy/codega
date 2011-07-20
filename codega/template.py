'''Handling templates and template sets.

A template is an object that - given the proper bindings - can create some kind of output. A template
set on the other hand is a collection of templates. All templates are accessed through a template set.

This module also contains MakoTemplateset which loads mako templates. Further templates can be
supported if needed.
'''
from UserDict import DictMixin

from error import TemplateNotFoundError
from stringio import StringIO

class Bindings(object, DictMixin):
    '''Template binding class.
    
    Simulates a dict with some confortability features, like attribute handling.

    Members:
    _data -- Bound variables
    _parent -- Parent binding
    '''

    _data = None
    _parent = None

    def __init__(self, parent = None, **init_data):
        self._data = dict(init_data)
        self._parent = parent

    @property
    def parent(self):
        return self._parent

    @property
    def root(self):
        return self._parent.root if self._parent is not None else self

    def __getattr__(self, name):
        if self._data.has_key(name):
            return self._data[name]

        if self._parent is not None:
            return self.parent[name]

        raise KeyError("Binding %s does not exist" % name)

    def __setattr__(self, name, value):
        if name in ('_data', '_parent'):
            super(Bindings, self).__setattr__(name, value)

        else:
            self._data[name] = value

    def __delattr__(self, name):
        try:
            del self._data[name]

        except KeyError:
            raise KeyError("Binding %s does not exist" % name)

    def extend(self, **data):
        ret = Bindings(parent = self, init_data = self._data)
        ret._data.update(data)

    __getitem__ = __getattr__
    __setitem__ = __setattr__
    __delitem__ = __delattr__

    def keys(self):
        return self._data.keys()

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
