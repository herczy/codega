from unittest import TestCase

from codega.version import Version

class VersionTest(TestCase):
    def test_initialize(self):
        self.assertEqual(Version('1', '0')._components, [1, 0])
        self.assertEqual(Version.load_from_string('1')._components, [1])
        self.assertEqual(Version.load_from_string('1.')._components, [1, 0])
        self.assertEqual(Version.load_from_string('1.0')._components, [1, 0])
        self.assertEqual(Version.load_from_string('1..0')._components, [1, 0, 0])

    def test_compare(self):
        self.assertTrue(Version.load_from_string('1.0') == Version.load_from_string('1'))
        self.assertTrue(Version.load_from_string('1.0') < Version.load_from_string('1.1'))
        self.assertTrue(Version.load_from_string('1.0') <= Version.load_from_string('1.1'))
        self.assertTrue(Version.load_from_string('1.1.2') > Version.load_from_string('1.1'))
