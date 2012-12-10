import os

from codega.source import SourceBase
from codega.alp import script, ast

from validator import Validator


class ScriptParser(SourceBase):
    '''ALP descriptor language parser. This is a thin wrapper
    so codega config scripts can also define ALP sources.'''

    def __init__(self):
        super(ScriptParser, self).__init__()

        # Circular include detection
        self.__circular = set()

    def load(self, resource, resource_locator=None, skip_validation=False):
        '''Load and validate ALP script'''

        if resource is not None:
            resource = resource_locator.find(resource)

        # Detect circular includes
        abspath = os.path.abspath(resource)

        if abspath in self.__circular:
            raise RuntimeError("Circular include detected (%s)" % abspath)

        self.__circular.add(abspath)

        # Load the file
        root = script.parse_file(resource)

        # Quick job: replace all includes with the proper
        # included sub-files.
        items = []
        for entry in root.body:
            if entry.ast_name == 'AlpInclude':
                path = entry.path[1:-1]

                included = self.load(path, resource_locator=resource_locator, skip_validation=True)
                items.extend(included.body)

            else:
                items.append(entry)

        root.body = root.body.replace(items)

        if not skip_validation:
            Validator.run(root)

        return root
