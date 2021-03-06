'''Mako template wrappers for codega

Dependencies: mako
'''

from mako.runtime import Context as ExternalMakoContext
from mako.lookup import TemplateLookup as ExternalMakoTemplateLookup
from mako.template import Template as ExternalMakoTemplate

from codega.stringio import StringIO

from codega.generator.template import TemplateGenerator
from codega.template import TemplateBase, TemplatesetBase
from codega import logger

from codega.indent import deindent


class MakoTemplate(TemplateBase):
    '''Wrapper for mako templates

    Members:
    _template -- Mako template
    '''

    _template = None

    def __init__(self, template):
        super(MakoTemplate, self).__init__()

        self._template = template

    def render(self, bindings):
        buf = StringIO()

        _binding_dict = dict(bindings)
        _binding_dict['template'] = self

        context = ExternalMakoContext(buf, **_binding_dict)

        try:
            self._template.render_context(context)

        except:
            logger.error('Rendering failed')
            raise

        return buf.getvalue()

    render.__doc__ = TemplateBase.render.__doc__


class MakoTemplateset(TemplatesetBase):
    '''Mako templateset (a wrapper to mako.lookup.TemplateLookup)

    Members:
    _lookup -- Mako lookup class
    '''

    _lookup = None

    def __init__(self, *args, **kwargs):
        super(MakoTemplateset, self).__init__()

        self._lookup = ExternalMakoTemplateLookup(*args, **kwargs)

    # TemplateCollection interface
    def get_template(self, name):
        fname, defname = name.rsplit(':', 1)

        tpl = self._lookup.get_template(fname)
        tpl = tpl.get_def(defname)

        return MakoTemplate(tpl)
    get_template.__doc__ = TemplatesetBase.get_template.__doc__

    def get_subset(self, name):
        return MakoTemplatesetFile(template_object=self._lookup.get_template(name))


class MakoTemplatesetFile(TemplatesetBase):
    '''Mako file-based templateset (a wrapper to mako.template.Template)

    Members:
    _template -- Mako master template
    '''

    _template = None

    def __init__(self, *args, **kwargs):
        super(MakoTemplatesetFile, self).__init__()

        if 'template_object' in kwargs:
            self._template = kwargs.pop('template_object')

        else:
            self._template = ExternalMakoTemplate(*args, **kwargs)

    # TemplateCollection interface
    def get_template(self, name):
        tpl = self._template.get_def(name)

        return MakoTemplate(tpl)
    get_template.__doc__ = TemplatesetBase.get_template.__doc__


class InlineMakoTemplate(MakoTemplate):
    '''Wrapper for mako templates.

    This class differs from MakoTemplate in that it parses the argument
    as a mako template, without using a template set.
    '''

    def __init__(self, data):
        super(InlineMakoTemplate, self).__init__(ExternalMakoTemplate(text=data))


class DocstringMakoTemplate(InlineMakoTemplate):
    '''Read a function or class docstring and parse it as a template'''

    def __init__(self, fun):
        super(DocstringMakoTemplate, self).__init__(deindent(fun.__doc__))


def inline(func):
    '''Creates a TemplateGenerator from the decorated function, using
    its docstring as an inline template source.'''

    template = DocstringMakoTemplate(func)
    return TemplateGenerator.factory(template)(func)
