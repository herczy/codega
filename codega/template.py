'''Handling templates and template sets.

A template is an object that - given the proper bindings - can create some kind of output. A template
set on the other hand is a collection of templates. All templates are accessed through a template set.

This module also contains MakoTemplateset which loads mako templates. Further templates can be
supported if needed.
'''
from UserDict import DictMixin

from mako.runtime import Context as ExternalMakoContext
from mako.lookup import TemplateLookup as ExternalMakoTemplateLookup
from mako.template import Template as ExternalMakoTemplate

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

#
# Mako-based template classes
#
class MakoTemplate(TemplateBase):
    '''Wrapper for mako templates

    Members:
    _template -- Mako template
    '''

    _template = None

    def __init__(self, name, template):
        super(MakoTemplate, self).__init__(name)

        self._template = template

    def render(self, bindings):
        buf = StringIO()

        _binding_dict = dict(bindings)
        _binding_dict['template'] = self

        context = ExternalMakoContext(buf, **_binding_dict)
        self._template.render_context(context)

        return buf.getvalue()

    render.__doc__ = TemplateBase.render.__doc__

class MakoTemplateset(TemplatesetBase):
    '''Mako templateset (a wrapper to mako.lookup.TemplateLookup)

    Members:
    _lookup -- Mako lookup class
    '''

    _lookup = None

    def __init__(self, *args, **kwargs):
        super(MakoLocator, self).__init__()

        self._lookup = ExternalMakoTemplateLookup(*args, **kwargs)

    # TemplateCollection interface
    def get_template(self, name):
        fname, defname = name.rsplit(':', 1)

        tpl = self._lookup.get_template(fname)
        tpl = tpl.get_def(defname)

        return MakoTemplate(name, tpl)
    get_template.__doc__ = TemplatesetBase.get_template.__doc__

#
# Inline mako template
#
class InlineMakoTemplate(MakoTemplate):
    '''Wrapper for mako templates.
    
    This class differs from MakoTemplate in that it parses the argument
    as a mako template, without using a template set.
    '''

    def __init__(self, name, data):
        super(InlineMakoTemplate, self).__init__(name, ExternalMakoTemplate(text = data))

class DocstringMakoTemplate(InlineMakoTemplate):
    '''Read a function or class docstring and parse it as a template'''

    def __init__(self, fun):
        tpl = fun.__doc__
        while tpl[0] == '\n':
            tpl = tpl[1:]

        indent = 0
        while tpl[indent] == ' ':
            indent += 1

        tpl_deindented = []
        for line in tpl.split('\n'):
            if line[:indent].strip():
                # Add line without de-indentation
                tpl_deindented.append(line)
                continue

            tpl_deindented.append(line[indent:])

        tpl = '\n'.join(tpl_deindented)
        super(DocstringMakoTemplate, self).__init__(fun.__name__, tpl)
