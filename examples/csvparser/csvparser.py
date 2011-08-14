'''Simple CSV parser example'''

import csv
from lxml import etree

from codega.source import FileSourceBase

class CSVParser(FileSourceBase):
    def load(self, resource):
        '''Load a CSV file and convert it into an XML structure'''

        resource = open(resource)
        root = etree.Element('csv')
        for row in csv.reader(resource):
            rowxml = etree.Element('row')

            for entry in row:
                entryxml = etree.Element('entry')
                entryxml.text = str(entry)
                rowxml.append(entryxml)

            root.append(rowxml)

        return etree.ElementTree(root)
