from unittest import TestCase

import re
import os
import os.path
from lxml import etree

import codega

from codega.source import XmlSource
from codega.config import *

def flatten(text):
    return ''.join(filter(lambda p: not p.isspace(), text))

def clean(text):
    res = flatten(text)

    # Be ignorant of versions
    res = re.sub(r'configversion="[0-9\.]*"', r'config', res)

    # From 1.1: rename filename to resource
    res = re.sub(r'name><filename>([^<]*)</filename>', r'name><resource>\1</resource>', res)

    return res

class TestVisitors(TestCase):
    def test_visitor(self):
        path = os.path.join(os.path.dirname(__file__), 'data')
        for item in os.listdir(path):
            fn, ext = os.path.splitext(item)
            if ext != '.xml':
                continue

            name, expect = os.path.splitext(fn)
            item_path = os.path.join(path, item)

            try:
                cfg = parse_config_file(item_path)

            except Exception, e:
                if expect != '.fail':
                    raise

                if not isinstance(e, ParseError):
                    raise

            else:
                self.assertEqual(expect, '.succ')

                if hasattr(self, 'check_%s' % name):
                    getattr(self, 'check_%s' % name)(cfg)

                fd, fn = make_tempfile()
                os.write(fd, save_config(cfg))
                parse_config_file(fn)

                self.assertEqual(clean(save_config(cfg)), clean(open(item_path).read()))

    def check_parse00(self, cfg):
        self.assertEqual(cfg.paths.destination, './')
        self.assertEqual(cfg.paths.paths, ['./'])

        self.assertEqual(cfg.sources['config'].name, 'config')
        self.assertEqual(cfg.sources['config'].resource, 'codega.xml')
        self.assertEqual(cfg.sources['config'].parser.module, 'codega.source')
        self.assertEqual(cfg.sources['config'].parser.reference, 'XmlSource')

        target = cfg.targets['config.txt']
        self.assertEqual(target.source, 'config')
        self.assertEqual(target.generator.module, 'dumper')
        self.assertEqual(target.generator.reference, 'DumpGenerator')
        self.assertEqual(target.filename, 'config.txt')

        self.assertEqual(target.settings.test0, 'value0')
        self.assertEqual(target.settings.test1.test2, 'value2')

class TestSettings(TestCase):
    def test_basic(self):
        settings = Settings()

        test0 = settings.add_container('a')
        test0['b'] = '2'
        test0['c'] = '3'

        settings.b = '4'
        settings.c = '5'

        self.assertEqual(settings.a.b, '2')
        self.assertEqual(settings.a.c, '3')

        self.assertEqual(settings.b, '4')
        self.assertEqual(settings.c, '5')

        del test0['b']

    def test_error(self):
        self.assertRaises(KeyError, Settings().__getitem__, 'x')
        self.assertRaises(KeyError, Settings().__delitem__, 'x')
        self.assertRaises(TypeError, Settings().__setitem__, 'x', 1)

class TestModuleReference(TestCase):
    def test_basic(self):
        mr = ModuleReference()
        self.assertEqual(mr.module, None)
        self.assertEqual(mr.reference, None)

        mr.load_from_string('codega.source:XmlSource')
        self.assertEqual(mr.module, 'codega.source')
        self.assertEqual(mr.reference, 'XmlSource')

        self.assertEqual(mr.load(ModuleLocator(codega)), XmlSource)

        self.assertRaises(ValueError, mr.load_from_string, 'c.g:--')
        self.assertRaises(ValueError, mr.load_from_string, 'c.g')
        self.assertRaises(ValueError, setattr, mr, 'module', '::')
        self.assertRaises(ValueError, setattr, mr, 'module', 'x::')
        self.assertRaises(ValueError, setattr, mr, 'module', ' ')
        self.assertRaises(ValueError, setattr, mr, 'module', '.x.y')
        self.assertRaises(ValueError, setattr, mr, 'reference', 'a.b')
        self.assertEqual(mr.module, 'codega.source')
        self.assertEqual(mr.reference, 'XmlSource')

        mr.load_from_string('a:b')
        self.assertRaises(ImportError, mr.load, ModuleLocator(codega))

        del mr.module
        del mr.reference
        self.assertEqual(mr.module, None)
        self.assertEqual(mr.reference, None)
