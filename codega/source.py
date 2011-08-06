'''Load from XML source

load() loads an XML eigther from a file or a string'''
from lxml import etree

from stringio import StringIO
from decorators import abstract

class SourceBase(object):
    '''A source should parse the supplied input and create an XML etree'''

    @abstract
    def load(self, resource):
        '''Load the given resource.

        This resource can be anything ranging from a filename, an XML etree, a
        Python module, etc.

        Arguments:
        resource -- The resource to be parsed
        '''

class FileSourceBase(SourceBase):
    '''A file source should parse a file (or list of files) and create an XML etree.'''

    def load_from_file(self, data = None, filename = None, locator = None):
        '''Load some file source.

        Arguments:
        data -- If set, the parser will parse this string
        filename -- If set, the parser will load this file
        locator -- A locator for finding filename
        '''

        if data is None and filename is None:
            raise ValueError("Function requires eighter a source or a filename, none specified")

        if data is not None and filename is not None:
            raise ValueError("Function requires eighter a source or a filename, both specified")

        if data is not None:
            source = StringIO(data)

        else:
            if locator is not None:
                filename = locator.find(filename)

            source = open(filename)

        return self.load(source)

class XmlSource(FileSourceBase):
    '''XML source. This is the default source'''

    def load(self, resource):
        return etree.parse(resource)

def validate_xml(xml, *args, **kwargs):
    '''Load an XSD source and validate XML with it

    Arguments:
    xml -- The XML to validate
    args, kwargs -- Arguments passed to load
    '''

    xsd = etree.XMLSchema(XmlSource().load_from_file(*args, **kwargs))
    xsd.assertValid(xml)
