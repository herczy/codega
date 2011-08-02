'''Mako template wrappers for codega

Dependencies: mako
'''

from mako.runtime import Context as ExternalMakoContext
from mako.lookup import TemplateLookup as ExternalMakoTemplateLookup
from mako.template import Template as ExternalMakoTemplate

from codega.generator import *
from codega.template import *
from codega import logger

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
            logger.error('Rendering failed, bindings = %r' % _binding_dict)
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

        return MakoTemplate(name, tpl)
    get_template.__doc__ = TemplatesetBase.get_template.__doc__

class InlineMakoTemplate(MakoTemplate):
    '''Wrapper for mako templates.
    
    This class differs from MakoTemplate in that it parses the argument
    as a mako template, without using a template set.
    '''

    def __init__(self, data):
        super(InlineMakoTemplate, self).__init__(ExternalMakoTemplate(text = data))

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
        super(DocstringMakoTemplate, self).__init__(tpl)

def inline(matcher = None, priority = PRI_BASE):
    '''Creates a FunctionGenerator from the decorated function, using
    its docstring as an inline template source.

    Arguments:
    matcher -- Generator matcher
    priority -- Generator function
    '''

    def __decorator(func):
        template = DocstringMakoTemplate(func)
        return TemplateGenerator(template, func, matcher = matcher, priority = priority)

    return __decorator
