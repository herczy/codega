from unittest import TestCase
import os
import os.path

from codega.source import XmlSource
from codega.rsclocator import FileResourceLocator

xml_content = """<?xml version="1.0" ?>\n<entry>Hello</entry>\n"""

class TestSource(TestCase):
    def setUp(self):
        self.source = XmlSource()

    def check(self, xml):
        root = xml.getroot()
        self.assertEqual(root.tag, 'entry')
        self.assertEqual(root.text, 'Hello')

    def test_load_data(self):
        self.check(self.source.load_from_file(data = xml_content))

    def test_load_file_without_locator(self):
        fd, name = make_tempfile()
        os.write(fd, xml_content)
        self.check(self.source.load_from_file(filename = name))

    def test_load_file_with_locator(self):
        loc = FileResourceLocator('/tmp')
        fd, name = make_tempfile()
        os.write(fd, xml_content)
        self.check(self.source.load_from_file(filename = os.path.basename(name), locator = loc))
