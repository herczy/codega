from unittest import TestCase, TestSuite

from codega.modules import *

class SourceModuleTest(TestCase):
    def test_source_module(self):
        mod = SourceModuleBase('test_source', 'test.xsd')
