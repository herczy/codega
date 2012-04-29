from unittest import TestCase

from codega.context import *

class TestContext(TestCase):
    def test_properties(self):
        class Target(object):
            settings = 3

        target = Target()
        ctx = Context(0, 1, target)

        self.assertEqual(ctx.config, 0)
        self.assertEqual(ctx.source, 1)
        self.assertEqual(ctx.target, target)
        self.assertEqual(ctx.settings, 3)

    def test_mapping(self):
        id = lambda *args: tuple(args)
        ctx = Context(0, 1, 2)
        self.assertEqual(ctx.map(id, [0, 1, 2]), [(0, ctx), (1, ctx), (2, ctx)])
        self.assertEqual(ctx.map(id, [0, 1, 2], filt_expr=lambda n: n == 1), [(1, ctx)])
