from codega.source import SourceBase
from codega.alp import script

from validator import Validator

class ScriptParser(SourceBase):
    '''ALP descriptor language parser. This is a thin wrapper
    so codega config scripts can also define ALP sources.'''

    def load(self, resource, resource_locator=None):
        '''Load and validate ALP script'''

        if resource_locator is not None:
            resource = resource_locator.find(resource)

        ast = script.parse(resource, open(resource).read())
        Validator.run(ast)

        return ast
