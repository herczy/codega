from unittest import TestCase
import os
import os.path

from codega.generator import *

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
        #return 'template %s context %r source = %r' % (bindings['name'], bindings['context'], bindings['source'])

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
    @FunctionGenerator.decorate(matcher = lambda s: s == 0)
    def generator_0(self, source, context):
        # No template, no document, this should be a FunctionGenerator
        return 'FunctionSubgenerator %r context %r' % (source, context)

    @TemplateGenerator.decorate(matcher = lambda s: s == 1, template = template_1)
    def generator_1(self, source, context):
        # Template explicitly specified
        return dict(name = 'testrunner!', source = source, context = context)

    @TemplateGenerator.decorate(matcher = lambda s: s == 2, template = template_2)
    def generator_2(self, source, context):
        # Template explicitly specified
        return dict(name = 'testrunner!', source = source, context = context)

class TestGenerators(TestCase):
    matcher = lambda self, src: src == 0

    def check(self, obj, source, context, expected):
        self.assertEqual(str(obj(source, context)), expected)

    def test_base(self):
        p = SimpleGenerator(matcher = self.matcher)
        self.assertTrue(p.priority == 0)
        self.assertTrue(p.parent == None)
        self.assertTrue(p.match(0))
        self.assertFalse(p.match(1))
        self.check(p, 0, 1, 'SimpleGenerator 0 1')
        self.assertRaises(ValueError, p, 1, None)

    def test_function(self):
        p = FunctionGenerator(fungen, matcher = self.matcher)
        self.assertTrue(p.priority == 0)
        self.assertTrue(p.parent == None)
        self.assertTrue(p.match(0))
        self.assertFalse(p.match(1))
        self.check(p, 0, 1, 'fungen 0 1')
        self.assertRaises(ValueError, p, 1, None)

    def test_template(self):
        tpl = TemplateMockup('template %(value)s %(context)s', 'value', 'context')
        p = TemplateGenerator(tpl, lambda x, c: dict(value = x, context = c), matcher = self.matcher)
        self.assertTrue(p.priority == 0)
        self.assertTrue(p.parent == None)
        self.assertTrue(p.match(0))
        self.assertFalse(p.match(1))
        self.check(p, 0, 1, 'template 0 1')
        self.assertRaises(ValueError, p, 1, None)

    def test_priority_generator(self):
        p0 = SimpleGenerator(matcher = lambda s: s == 0)
        p1 = SimpleGenerator(matcher = lambda s: s == 1)
        p2 = SimpleGenerator(matcher = lambda s: s == 2)
        p3 = FunctionGenerator(fungen, matcher = lambda s: s == 0, priority = PRI_LOW)
        p = PriorityGenerator()
        self.assertTrue(p.priority == 0)
        self.assertTrue(p.parent == None)
        p.register(p0)
        p.register(p1)
        p.register(p2)
        p.register(p3)

        self.assertTrue(p0.priority == PRI_BASE)
        self.assertTrue(p0.parent == p)
        self.assertTrue(p1.priority == PRI_BASE)
        self.assertTrue(p1.parent == p)
        self.assertTrue(p2.priority == PRI_BASE)
        self.assertTrue(p2.parent == p)
        self.assertTrue(p3.priority == PRI_LOW)
        self.assertTrue(p3.parent == p)

        self.assertTrue(p.match(0))
        self.assertTrue(p.match(1))
        self.assertTrue(p.match(2))
        self.assertFalse(p.match(3))

        self.check(p, 0, 1, 'SimpleGenerator 0 1')
        self.check(p, 1, 1, 'SimpleGenerator 1 1')
        self.check(p, 2, 1, 'SimpleGenerator 2 1')
        self.assertRaises(ValueError, p, 4, None)

    def test_object_generator(self):
        p = MyObjectGenerator()
        self.assertTrue(p.priority == 0)
        self.assertTrue(p.parent == None)

        self.assertTrue(p.match(0))
        self.assertTrue(p.match(1))
        self.assertTrue(p.match(2))
        self.assertFalse(p.match(3))

        self.check(p, 0, 1, "FunctionSubgenerator 0 context 1")
        self.check(p, 1, 1, "template #1 (context = 1, source = 1, name = 'testrunner!'")
        self.check(p, 2, 1, "template #2 (context = 1, source = 2, name = 'testrunner!'")
        self.assertRaises(ValueError, p, 4, None)
