'''Load from XML source

load() loads an XML eigther from a file or a string'''
from lxml import etree

from stringio import StringIO
from decorators import abstract

class SourceBase(object):
    '''A source should parse the supplied input and create an XML etree'''

    @abstract
    def load(self, resource, resource_locator = None):
        '''Load the given resource.

        This resource can be anything ranging from a filename, an XML etree, a
        Python module, etc.

        Arguments:
        resource -- The resource to be parsed
        resource_locator -- An optional ResourceLocatorBase for locating the resource
        '''

class FileSourceBase(SourceBase):
    '''A file source should parse a file (or list of files) and create an XML etree.'''

    def load(self, resource, resource_locator = None):
        '''Load some file source.'''

        if resource_locator is not None:
            resource = resource_locator.find(resource)

        return self.load_fileobj(open(resource))

class XmlSource(FileSourceBase):
    '''XML source. This is the default source'''

    def load_fileobj(self, fileobj):
        return etree.parse(fileobj)

class NullSource(SourceBase):
    '''This source parses nothing and returns nothing'''

    def load(self, resource, resource_locator = None):
        return etree.ElementTree()

def validate_xml(xml, *args, **kwargs):
    '''Load an XSD source and validate XML with it

    Arguments:
    xml -- The XML to validate
    args, kwargs -- Arguments passed to load
    '''

    xsd = etree.XMLSchema(XmlSource().load(*args, **kwargs))
    xsd.assertValid(xml)
