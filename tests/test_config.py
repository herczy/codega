from unittest import TestCase, TestSuite
import os
import os.path
import tempfile

from codega.rsclocator import FileResourceLocator
from codega.config import *

class XMLMockup(object):
    def __init__(self, tag, text = '', **attributes):
        self.tag = tag
        self.attrib = attributes
        self.text = text

        self.children = []

    def add_child(self, child):
        self.children.append(child)
        return child

    def __iter__(self):
        return iter(self.children)

    def find(self, name):
        for ch in self.children:
            if ch.tag == name:
                return ch

class TestConfigSettings(TestCase):
    def setUp(self):
        self.xml = XMLMockup('settings')
        self.xml.add_child(XMLMockup('entry', text = 'test0value', name = 'test0'))
        cont = self.xml.add_child(XMLMockup('container', name = 'test1'))
        cont.add_child(XMLMockup('entry', text = 'test2value', name = 'test2'))

        self.settings = ConfigSettings(self, self.xml)

    def test_values(self):
        self.assertEqual(self.settings.test0, 'test0value')
        self.assertEqual(self.settings.test1.test2, 'test2value')
        self.assertTrue(isinstance(self.settings.test1, ConfigSettings))

        self.assertRaises(KeyError, getattr, self.settings, 'test3')

class TestConfigSource(TestCase):
    def setUp(self):
        class ParentMockup(object):
            @property
            def locator(self):
                return FileResourceLocator('/tmp')

        self.xml = XMLMockup('source')
        self.xml.add_child(XMLMockup('name', 'test'))
        self.xml.add_child(XMLMockup('filename', 'testfile'))
        self.source = ConfigSource(ParentMockup(), self.xml)

    def test_values(self):
        self.assertEqual(self.source.name, 'test')
        self.assertEqual(self.source.filename, 'testfile')

    def test_mtime(self):
        self.assertEqual(self.source.mtime, 0)

        fd, fn = tempfile.mkstemp()
        self.source.filename = fn
        self.assertNotEqual(self.source.mtime, 0)
