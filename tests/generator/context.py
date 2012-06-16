from unittest import TestCase

from codega.generator.context import *

from common import SimpleGenerator

class TestContext(TestCase):
    def test_properties(self):
        '''The context object properties work properly.'''

        context = Context('source', 'target', 'generator', 'parser', { 'settings' : 1 })

        self.assertEqual(context.source, 'source')
        self.assertEqual(context.target, 'target')
        self.assertEqual(context.generator, 'generator')
        self.assertEqual(context.parser, 'parser')
        self.assertEqual(context.settings, { 'settings' : 1 })

    def test_mapping(self):
        '''The context mapper method generates all sources.'''

        context = Context('source', 'target', 'generator', 'parser', { 'settings' : 1 })

        gen = SimpleGenerator()
        sources = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        context.map(gen, sources)
        self.assertEqual(gen.generate_access_count, 10)

        gen = SimpleGenerator()
        context.map(gen, sources, filt_expr=lambda x: x % 2 == 0)
        self.assertEqual(gen.generate_access_count, 5)
