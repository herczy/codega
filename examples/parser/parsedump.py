from codega.source import *
from codega.generator.base import GeneratorBase

from lxml import etree

class TestParser(FileSourceBase):
    def load_fileobj(self, fileobj):
        res = etree.Element('root')
        for ln in fileobj:
            lnobj = etree.Element('line')
            lnobj.text = ln.strip()

            res.append(lnobj)

        return etree.ElementTree(res)
