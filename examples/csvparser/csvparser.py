'''Simple CSV parser example'''

import csv
from lxml import etree

from codega.source import FileSourceBase

class CSVParser(FileSourceBase):
    def load_fileobj(self, fileobj):
        '''Load a CSV file and convert it into an XML structure'''

        root = etree.Element('csv')
        for row in csv.reader(fileobj):
            rowxml = etree.Element('row')

            for entry in row:
                entryxml = etree.Element('entry')
                entryxml.text = str(entry)
                rowxml.append(entryxml)

            root.append(rowxml)

        return etree.ElementTree(root)
