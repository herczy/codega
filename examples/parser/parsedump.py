from codega.source import SourceBase
from codega.generator import GeneratorBase

from lxml import etree

class TestParser(SourceBase):
    def load_from_fileobj(self, fileobj):
        res = etree.Element('root')
        for ln in fileobj:
            lnobj = etree.Element('line')
            lnobj.text = ln.strip()

            res.append(lnobj)

        return etree.ElementTree(res)
