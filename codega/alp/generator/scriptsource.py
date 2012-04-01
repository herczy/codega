from codega.source import SourceBase
from codega.alp import script

from flatten import flatten
from validator import Validator

class ScriptParser(SourceBase):
    def load(self, resource, resource_locator=None):
        '''Load and validate ALP script'''

        if resource_locator is not None:
            resource = resource_locator.find(resource)

        ast = flatten(script.parse(resource, open(resource).read()), script.AstBaseClass)
        Validator.run(ast)

        return ast
