'''Load from XML source

load() loads an XML eigther from a file or a string'''
from lxml import etree

def load(data = None, filename = None, locator = None):
    '''Load an XML file

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

    return etree.parse(source).getroot()
