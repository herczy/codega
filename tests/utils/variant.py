from unittest import TestCase

from codega.utils.variant import *

class TestVariant(TestCase):
    def test_variant_matcher(self):
        '''The variant matcher checks if the context has a variant set to a proper value.'''

        var = variant('test')
        obj0 = type('obj0', (object,), dict(variant='test'))
        obj1 = type('obj1', (object,), dict(variant='test2'))
        obj2 = type('obj2', (object,), dict())

        self.assertTrue(var(None, obj0))
        self.assertFalse(var(None, obj1))
        self.assertFalse(var(None, obj2))

    def test_use_variant(self):
        '''The variant can be defined in a scope.'''

        obj = type('obj', (object,), dict())
        with use_variant(obj, 'test'):
            self.assertTrue(hasattr(obj, 'variant'))
            self.assertEqual(obj.variant, 'test')

            with use_variant(obj, 'subscope'):
                self.assertTrue(hasattr(obj, 'variant'))
                self.assertEqual(obj.variant, 'subscope')

            self.assertTrue(hasattr(obj, 'variant'))
            self.assertEqual(obj.variant, 'test')

        self.assertFalse(hasattr(obj, 'variant'))

    def test_get_variant(self):
        '''The variant can be explicitly queried.'''

        obj = type('obj', (object,), dict(variant='test'))()
        self.assertEqual(get_variant(obj), 'test')

        obj = type('obj', (object,), dict())()
        self.assertEqual(get_variant(obj), None)
