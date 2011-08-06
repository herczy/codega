from codega.source import *
from codega.generator import GeneratorBase

from lxml import etree

class TestParser(FileSourceBase):
    def load(self, resource):
        res = etree.Element('root')
        for ln in resource:
            lnobj = etree.Element('line')
            lnobj.text = ln.strip()

            res.append(lnobj)

        return etree.ElementTree(res)
