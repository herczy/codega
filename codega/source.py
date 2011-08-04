'''Load from XML source

load() loads an XML eigther from a file or a string'''
from lxml import etree

from stringio import StringIO
from decorators import abstract

class SourceBase(object):
    '''A source should parse a file (or list of files) and create an XML etree.'''

    @abstract
    def load_from_fileobj(self, fileobj):
        '''Load XML etree from the supplied file object

        Arguments:
        fileobj -- Raw data for source. Is a file object (StringIO, file, etc.)
        '''

    def load(self, data = None, filename = None, locator = None):
        '''Load some source

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

        return self.load_from_fileobj(source)

    def validate(self, xml, *args, **kwargs):
        '''Load an XSD source and validate XML with it

        Arguments:
        xml -- The XML to validate
        args, kwargs -- Arguments passed to load
        '''

        xsd = etree.XMLSchema(self.load(*args, **kwargs))
        xsd.assertValid(xml)

class XmlSource(SourceBase):
    '''XML source. This is the default source'''

    def load_from_fileobj(self, fileobj):
        return etree.parse(fileobj)
