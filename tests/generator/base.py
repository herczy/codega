from unittest import TestCase

from codega.generator.base import *

from common import SimpleGenerator

class TestBase(TestCase):
    def test_validate(self):
        '''Base generators have validator functions.'''

        self.assertEqual(GeneratorBase().validate('source', 'context'), None)

    def test_generate(self):
        '''Base generators generate function is abstract.'''

        self.assertRaises(NotImplementedError, GeneratorBase().generate, 'source', 'context')

    def test_call(self):
        '''Calling a generator as a functor validates and generates input.'''

        gen = SimpleGenerator()
        gen(123, 456)

        self.assertEqual(gen.validate_lastrun.args, (123, 456))
        self.assertEqual(gen.generate_lastrun.args, (123, 456))

    def test_string(self):
        '''Generator can be converted to a string.'''

        gen = SimpleGenerator()

        self.assertEqual(str(gen), 'generator:%d' % id(gen))

    def test_represent(self):
        '''Generator can be converted to a representation.'''

        gen = SimpleGenerator()

        self.assertEqual(repr(gen), 'SimpleGenerator(generator:%d)' % id(gen))
