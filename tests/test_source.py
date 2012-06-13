from unittest import TestCase
import os.path

from codega.source import XmlSource
from codega.rsclocator import FileResourceLocator

from common import make_tempfile

xml_content = """<?xml version="1.0" ?>\n<entry>Hello</entry>\n"""

class TestSource(TestCase):
    def setUp(self):
        self.source = XmlSource()

    def check(self, xml):
        root = xml.getroot()
        self.assertEqual(root.tag, 'entry')
        self.assertEqual(root.text, 'Hello')

    def test_load_file(self):
        with make_tempfile() as (fd, name):
            os.write(fd, xml_content)
            self.check(self.source.load(resource=name))
