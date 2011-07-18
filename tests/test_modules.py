from unittest import TestCase, TestSuite
import os, os.path

from codega.modules import *
from codega.source import load
from codega.rsclocator import FileResourceLocator

class TestModuleBase(TestCase):
    info = { 'a' : 1, 'b' : 2 }

    def setUp(self):
        self.base = ModuleBase('test', info = self.info)

    def test_locator(self):
        self.base.set_locator(1)
        self.assertEqual(self.base.locator, 1)

    def test_info(self):
        self.assertEqual(self.base.info.a, 1)
        self.assertEqual(self.base.info.b, 2)
        self.assertRaises(KeyError, getattr, self.base.info, 'c')

class TestModuleGeneratorBase(TestModuleBase):
    def setUp(self):
        def __():
            def res(source, target):
                print >>target, 'Hello', source

            return res

        self.base = GeneratorModuleBase('test', { 'generate' : __ }, info = self.info)

        xsd_file = 'config.xsd'
        self.base_validated = GeneratorModuleBase('test', { 'generate' : __ }, validator = xsd_file, info = self.info)
        self.base_validated.set_locator(FileResourceLocator([ os.path.join(os.path.dirname(__file__), '..', 'codega') ]))

    def test_validate(self):
        xml = load(data = '''<?xml version="1.0" ?>
<config version="1.0">
    <paths>
        <target>a</target>
        <path>b</path>
    </paths>
    <source>
        <name>c</name>
        <filename>d</filename>
    </source>
    <target>
        <source>e</source>
        <generator>f</generator>
        <target>g</target>
    </target>
</config>''')

        self.assertTrue(self.base.validate(xml))
        self.assertTrue(self.base_validated.validate(xml))

    def test_generate(self):
        try:
            from cStringIO import StringIO

        except ImportError, e:
            if str(e) != 'No module cStringIO':
                raise

            from StringIO import StringIO

        out = StringIO()
        self.base.generate(0, 'generate', out)
        self.assertEqual(out.getvalue(), 'Hello 0\n')

        out = StringIO()
        self.assertRaises(KeyError, self.base.generate, 1, 'notfound', out)
        self.assertEqual(out.getvalue(), '')

class TestModuleFilterBase(TestModuleBase):
    def setUp(self):
        self.base = FilterModuleBase('test', lambda s: ''.join(reversed(s)), info = self.info)

    def test_filter(self):
        self.assertEqual(self.base.filter('abc'), 'cba')
