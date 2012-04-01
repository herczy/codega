from codega.source import FileSourceBase

from alplang import module
from flatten import flatten
from validator import Validator

class ScriptParser(FileSourceBase):
    def load_fileobj(self, fileobj):
        '''Load a CSV file and convert it into an XML structure'''

        ast = flatten(module.parse('input', fileobj.read()))
        Validator.run(ast)

        return ast
