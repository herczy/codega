from unittest import TestCase, TestSuite

import os
import os.path
from lxml import etree

from codega.config import *

def flatten(text):
    return ''.join(filter(lambda p: not p.isspace(), text))

def coldiff(t0, t1):
    if t0 == t1:
        return

    for i in xrange(min(len(t0), len(t1))):
        if t0[i] != t1[i]:
            print i, t0[i], t1[i]
            break

    print 'length'

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
                cfg = parse_config(filename = item_path)

            except Exception, e:
                if expect != '.fail':
                    raise

            else:
                self.assertEqual(expect, '.succ')

                if hasattr(self, 'check_%s' % name):
                    getattr(self, 'check_%s' % name)(cfg)

                parse_config(data = save_config(cfg))
                self.assertEqual(flatten(save_config(cfg)), flatten(open(item_path).read()))

    def check_parse00(self, cfg):
        self.assertEqual(cfg.paths.destination, './')
        self.assertEqual(cfg.paths.paths, ['./'])

        self.assertEqual(cfg.sources['config'].name, 'config')
        self.assertEqual(cfg.sources['config'].filename, 'codega.xml')
        self.assertEqual(cfg.sources['config'].parser.module, 'codega.source')
        self.assertEqual(cfg.sources['config'].parser.reference, 'XmlSource')

        target = cfg.targets['config.txt']
        self.assertEqual(target.source, 'config')
        self.assertEqual(target.generator.module, 'dumper')
        self.assertEqual(target.generator.reference, 'DumpGenerator')
        self.assertEqual(target.filename, 'config.txt')

        self.assertEqual(target.settings.test0, 'value0')
        self.assertEqual(target.settings.test1.test2, 'value2')
