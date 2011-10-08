'''AST loader

With this, we can load AST specifications like normal Python modules. The AST spec modules
should have the extension <modulename>.py.ast
'''

import sys
import os.path

from module import ModuleCreator
from error import AstError

def load_file(file, name = None):
    from codega.logger import error

    from spec import Lexer, Parser
    from validators import validators

    if name is None:
        name = os.path.splitext(os.path.basename(file))[0]

    module = ModuleCreator(name)
    module.load_validator_dict(validators)

    lexer = Lexer()
    lexer.input(open(file, 'r').read())

    parser = Parser(lexer)
    parser.parse(module)

    has_error = False
    for err in lexer.errors:
        error(str(err))
        has_error = True

    for err in parser.errors:
        error(str(err))
        has_error = True

    if has_error:
        raise AstError("Cannot parse file %s" % file)

    return module.module

class AstLoader(object):
    def __init__(self, filename):
        self._filename = filename

    def load_module(self, name):
        return load_file(self._filename, name = name)

class AstFinder(object):
    def find_module(self, fullname, path = None):
        path_list = None
        if path is None:
            path_list = iter(sys.path)

        else:
            path_list = iter(path)

        name = fullname.split('.')[-1]

        checkname = '%s.py.ast' % name
        for cur in path_list:
            fullpath = os.path.join(cur, checkname)

            if os.path.isfile(fullpath):
                return AstLoader(fullpath)

def init():
    import sys
    sys.meta_path.append(AstFinder())
