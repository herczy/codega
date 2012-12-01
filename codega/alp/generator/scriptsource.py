from codega.source import SourceBase
from codega.alp import script

from validator import Validator


def parse(fileobj, name='<unknown>'):
    ast = script.parse(name, fileobj.read())
    Validator.run(ast)
    return ast


class ScriptParser(SourceBase):
    '''ALP descriptor language parser. This is a thin wrapper
    so codega config scripts can also define ALP sources.'''

    def load(self, resource, resource_locator=None):
        '''Load and validate ALP script'''

        if resource_locator is not None:
            resource = resource_locator.find(resource)

        return parse(open(resource), name=resource)
