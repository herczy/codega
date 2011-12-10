import os.path

from codega.error import ParseError
from codega.source import SourceBase

from xml import ConfigXmlSource
from custom import ConfigCustomSource

class ConfigLoader(SourceBase):
    def decide_format(self, filename):
        filename = os.path.basename(filename)
        if filename == 'codega':
            return ConfigCustomSource()

        ext = os.path.splitext(filename)[1]

        if ext == '.xml':
            return ConfigXmlSource()

        elif ext == '.codega':
            return ConfigCustomSource()

        else:
            raise ParseError('Cannot recognize file format of %s' % filename, 0)

    def load(self, resource, resource_locator = None):
        loader = self.decide_format(resource)

        if resource_locator is not None:
            resource = resource_locator.find(resource)

        return loader.load_fileobj(open(resource))
