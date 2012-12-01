'''
Inline ALP runner. Using this you can create a parser without
generating (manually, at least) the output file.
'''

import types
import os.path

from codega.context import Context

from codega.alp.generator import scriptsource, scriptgen


def load(alpfile, alpname='<alp>', modname='alp'):
    ast = scriptsource.parse(alpfile, name=alpname)
    context = Context(None, None, None)
    code = compile(scriptgen.main_generator(ast, context), alpname, 'exec')

    retmod = types.ModuleType(modname)
    exec code in retmod.__dict__

    return retmod


def load_file(alpfile):
    modname = os.path.splitext(os.path.basename(alpfile))[0]
    return load(open(alpfile), alpname=alpfile, modname=modname)
