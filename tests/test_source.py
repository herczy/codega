from unittest import TestCase, TestSuite
import os
import os.path
import tempfile

from codega.source import load
from codega.rsclocator import FileResourceLocator

xml_content = """<?xml version="1.0" ?>\n<entry>Hello</entry>\n"""

class TestSource(TestCase):
    def check(self, xml):
        self.assertEqual(xml.tag, 'entry')
        self.assertEqual(xml.text, 'Hello')

    def test_load_data(self):
        self.check(load(data = xml_content))

    def test_load_file_without_locator(self):
        fd, name = tempfile.mkstemp()
        os.write(fd, xml_content)
        self.check(load(filename = name))

    def test_load_file_with_locator(self):
        loc = FileResourceLocator(['/tmp'])
        fd, name = tempfile.mkstemp()
        os.write(fd, xml_content)
        self.check(load(filename = os.path.basename(name), locator = loc))
