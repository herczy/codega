from unittest import TestCase, TestSuite
import os
import os.path
import tempfile

from codega.generator import *

class SimpleGenerator(GeneratorBase):
    def generate(self, source, target, context):
        print >>target, 'SimpleGenerator', repr(source), repr(context)

def fungen(source, target, context):
    print >>target, 'fungen', repr(source), repr(context)

class TemplateMockup(object):
    def render(self, bindings):
        return 'template %r' % bindings

class TemplateMockupOther(object):
    def render(self, bindings):
        return 'template %s context %r source = %r' % (bindings['name'], bindings['context'], bindings['source'])

class FileMockup(object):
    def __init__(self):
        self.value = ''

    def write(self, data):
        self.value += data

    def __str__(self):
        return self.value

class MyObjectGenerator(ObjectGenerator):
    @generator(matcher = lambda s: s == 0)
    def generator_0(self, source, target, context):
        # No template, no document, this should be a FunctionGenerator
        print >>target, 'FunctionSubgenerator %r context %r' % (source, context)

    @generator(matcher = lambda s: s == 1)
    def generator_1(self, source, context):
        '''
        Hello ${name}! source = ${repr(source)} context = ${cgctx}
        '''

        # No template but docstring exists, this should be a TemplateGenerator
        # with an inline mako template (DocstringMakoTemplate)
        return dict(name = 'testrunner!', source = source, cgctx = context)

    @generator(matcher = lambda s: s == 2, template = TemplateMockupOther())
    def generator_2(self, source, context):
        # Template explicitly specified
        return dict(name = 'testrunner!', source = source, context = context)

class TestGenerators(TestCase):
    matcher = lambda self, src: src == 0

    def check(self, obj, source, context, expected):
        dst = FileMockup()
        obj(source, dst, context)
        self.assertEqual(str(dst), expected)

    def test_base(self):
        p = SimpleGenerator(matcher = self.matcher)
        self.assertTrue(p.priority == 0)
        self.assertTrue(p.parent == None)
        self.assertTrue(p.match(0))
        self.assertFalse(p.match(1))
        self.check(p, 0, 1, 'SimpleGenerator 0 1\n')
        self.assertRaises(ValueError, p, 1, None, None)

    def test_function(self):
        p = FunctionGenerator(fungen, matcher = self.matcher)
        self.assertTrue(p.priority == 0)
        self.assertTrue(p.parent == None)
        self.assertTrue(p.match(0))
        self.assertFalse(p.match(1))
        self.check(p, 0, 1, 'fungen 0 1\n')
        self.assertRaises(ValueError, p, 1, None, None)

    def test_template(self):
        tpl = TemplateMockup()
        p = TemplateGenerator(tpl, lambda x, c: [x, c], matcher = self.matcher)
        self.assertTrue(p.priority == 0)
        self.assertTrue(p.parent == None)
        self.assertTrue(p.match(0))
        self.assertFalse(p.match(1))
        self.check(p, 0, 1, 'template [0, 1]')
        self.assertRaises(ValueError, p, 1, None, None)

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

        self.check(p, 0, 1, 'SimpleGenerator 0 1\n')
        self.check(p, 1, 1, 'SimpleGenerator 1 1\n')
        self.check(p, 2, 1, 'SimpleGenerator 2 1\n')
        self.assertRaises(ValueError, p, 4, None, None)

    def test_object_generator(self):
        p = MyObjectGenerator()
        self.assertTrue(p.priority == 0)
        self.assertTrue(p.parent == None)

        self.assertTrue(p.match(0))
        self.assertTrue(p.match(1))
        self.assertTrue(p.match(2))
        self.assertFalse(p.match(3))

        self.check(p, 0, 1, 'FunctionSubgenerator 0 context 1\n')
        self.check(p, 1, 1, 'Hello testrunner!! source = 1 context = 1\n')
        self.check(p, 2, 1, 'template testrunner! context 1 source = 2')
        self.assertRaises(ValueError, p, 4, None, None)
