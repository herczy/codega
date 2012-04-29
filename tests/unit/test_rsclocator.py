import os.path

from unittest import TestCase

from codega.rsclocator import FileResourceLocator, ModuleLocator, FallbackLocator
from codega.error import ResourceError

path0 = os.path.dirname(__file__)
path1 = os.path.dirname(path0)

def test_list_base(self):
    for rsc in self.locator.list_resources():
        self.assertTrue(self.locator.find(rsc))

class FileLocatorTest(TestCase):
    def setUp(self):
        self.locator = FileResourceLocator(path0)

    def test_find(self):
        self.assertEqual(self.locator.find('test_rsclocator.py'), os.path.join(path0, 'test_rsclocator.py'))
        self.assertEqual(self.locator.find('../functional/test_examples.py'), os.path.join(path0, '..', 'functional', 'test_examples.py'))

        self.assertRaises(ResourceError, self.locator.find, 'aaaaaaa')

    test_list = test_list_base

class ModuleLocatorTest(TestCase):
    def setUp(self):
        self.module = __import__('codega.rsclocator')
        self.path = os.path.dirname(self.module.__file__)
        self.locator = ModuleLocator(self.module)

    def test_find(self):
        self.assertEqual(self.locator.find('rsclocator.py'), os.path.join(self.path, 'rsclocator.py'))

    test_list = test_list_base

class FallbackLocatorTest(TestCase):
    def setUp(self):
        self.module = __import__('codega.rsclocator')
        self.path = os.path.dirname(self.module.__file__)
        self.locator = FallbackLocator([ FileResourceLocator(path0), FileResourceLocator(path1), ModuleLocator(self.module) ])

    def test_find(self):
        self.assertEqual(self.locator.find('test_rsclocator.py'), os.path.join(path0, 'test_rsclocator.py'))
        self.assertEqual(self.locator.find('../run_test.py'), os.path.join(path1, '..', 'run_test.py'))
        self.assertEqual(self.locator.find('rsclocator.py'), os.path.join(self.path, 'rsclocator.py'))

    test_list = test_list_base
