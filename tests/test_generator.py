from unittest import TestCase

from codega.generator.base import GeneratorBase
from codega.generator.function import FunctionGenerator
from codega.generator.template import TemplateGenerator
from codega.generator.priority import PriorityGenerator, PRI_LOW
from codega.generator.object import ObjectGenerator, generator, match

class SimpleGenerator(GeneratorBase):
    def generate(self, source, context):
        return 'SimpleGenerator %r %r' % (source, context)

def fungen(source, context):
    return 'fungen %r %r' % (source, context)

class TemplateMockup(object):
    def __init__(self, fmt, *keylist):
        self._fmt = fmt
        self._keylist = keylist

    def render(self, bindings):
        bound = dict((k, bindings[k]) for k in self._keylist)
        return self._fmt % bound

class FileMockup(object):
    def __init__(self):
        self.value = ''

    def write(self, data):
        self.value += data

    def __str__(self):
        return self.value

template_1 = TemplateMockup('template #1 (context = %(context)r, source = %(source)r, name = %(name)r', 'context', 'source', 'name')
template_2 = TemplateMockup('template #2 (context = %(context)r, source = %(source)r, name = %(name)r', 'context', 'source', 'name')

class MyObjectGenerator(ObjectGenerator):
    @match(lambda s, c: s == 0)
    @generator(FunctionGenerator.factory)
    def generator_0(self, source, context):
        # No template, no document, this should be a FunctionGenerator
        return 'FunctionSubgenerator %r context %r' % (source, context)

    @match(lambda s, c: s == 1)
    @generator(TemplateGenerator.factory(template_1))
    def generator_1(self, source, context):
        # Template explicitly specified
        return dict(name = 'testrunner!', source = source, context = context)

    @match(lambda s, c: s == 2)
    @generator(TemplateGenerator.factory(template_2))
    def generator_2(self, source, context):
        # Template explicitly specified
        return dict(name = 'testrunner!', source = source, context = context)

class TestGenerators(TestCase):
    matcher = lambda self, src, context: src == 0

    def check(self, obj, source, context, expected):
        self.assertEqual(str(obj(source, context)), expected)

    def test_base(self):
        p = SimpleGenerator()
        self.check(p, 0, 1, 'SimpleGenerator 0 1')
        self.check(p, 1, 2, 'SimpleGenerator 1 2')

    def test_function(self):
        p = FunctionGenerator(fungen)
        self.check(p, 0, 1, 'fungen 0 1')
        self.check(p, 1, 2, 'fungen 1 2')

    def test_template(self):
        tpl = TemplateMockup('template %(value)s %(context)s', 'value', 'context')
        p = TemplateGenerator(tpl, lambda x, c: dict(value = x, context = c))
        self.check(p, 0, 1, 'template 0 1')
        self.check(p, 1, 2, 'template 1 2')

    def test_priority_generator(self):
        p0 = SimpleGenerator()
        p1 = SimpleGenerator()
        p2 = SimpleGenerator()
        p3 = FunctionGenerator(fungen)

        p = PriorityGenerator()
        p.register(p0, matcher = lambda s, c: s == 0 and c == 1)
        p.register(p1, matcher = lambda s, c: s == 1)
        p.register(p2, matcher = lambda s, c: s == 2)
        p.register(p3, matcher = lambda s, c: s == 0, priority = PRI_LOW)

        self.assertTrue(len(p._generators) == 4)

        self.check(p, 0, 1, 'SimpleGenerator 0 1')
        self.check(p, 1, 1, 'SimpleGenerator 1 1')
        self.check(p, 2, 1, 'SimpleGenerator 2 1')
        self.check(p, 0, 2, 'fungen 0 2')
        self.assertRaises(ValueError, p, 4, None)

    def test_object_generator(self):
        p = MyObjectGenerator()

        self.check(p, 0, 1, "FunctionSubgenerator 0 context 1")
        self.check(p, 1, 1, "template #1 (context = 1, source = 1, name = 'testrunner!'")
        self.check(p, 2, 1, "template #2 (context = 1, source = 2, name = 'testrunner!'")
        self.assertRaises(ValueError, p, 4, None)
