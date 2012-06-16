from unittest import TestCase

from codega.generator.function import *

class TestFunction(TestCase):
    def setUp(self):

        self._funcgen = FunctionGenerator(lambda source, context:(source, context))

    def test_function_generate(self):
        '''Function generators have the generate method defined.'''

        self.assertEqual(self._funcgen.generate(1, 2), (1, 2))
        self.assertEqual(self._funcgen(1, 2), (1, 2))

    def test_function_generator_factory(self):
        '''Function generator factory method works.'''

        gen = FunctionGenerator.factory(lambda * args: args)
        self.assertEqual(gen.generate(1, 2), (1, 2))
        self.assertEqual(gen(1, 2), (1, 2))
