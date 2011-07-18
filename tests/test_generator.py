from unittest import TestCase, TestSuite
import os
import os.path
import tempfile

from codega.generator import *

class SimpleGenerator(GeneratorBase):
    def generate(self, source, target):
        print >>target, 'SimpleGenerator', repr(source)

def fungen(source, target):
    print >>target, 'fungen', repr(source)

class TemplateMockup(object):
    def render(self, bindings):
        return 'template %r' % bindings

class TemplateMockupOther(object):
    def render(self, bindings):
        return 'template %s source = %r' % (bindings['name'], bindings['source'])

class FileMockup(object):
    def __init__(self):
        self.value = ''

    def write(self, data):
        self.value += data

    def __str__(self):
        return self.value

class MyObjectGenerator(ObjectGenerator):
    @generator(matcher = lambda s: s == 0)
    def generator_0(self, source, target):
        # No template, no document, this should be a FunctionGenerator
        print >>target, 'FunctionSubgenerator %r' % source

    @generator(matcher = lambda s: s == 1)
    def generator_1(self, source):
        '''
        Hello ${name}! source = ${repr(source)}
        '''

        # No template but docstring exists, this should be a TemplateGenerator
        # with an inline mako template (DocstringMakoTemplate)
        return dict(name = 'testrunner!', source = source)

    @generator(matcher = lambda s: s == 2, template = TemplateMockupOther())
    def generator_2(self, source):
        # Template explicitly specified
        return dict(name = 'testrunner!', source = source)

class TestGenerators(TestCase):
    matcher = lambda self, src: src == 0

    def check(self, obj, source, expected):
        dst = FileMockup()
        obj(source, dst)
        self.assertEqual(str(dst), expected)

    def test_base(self):
        p = SimpleGenerator(matcher = self.matcher)
        self.assertTrue(p.priority == 0)
        self.assertTrue(p.parent == None)
        self.assertTrue(p.match(0))
        self.assertFalse(p.match(1))
        self.check(p, 0, 'SimpleGenerator 0\n')
        self.assertRaises(ValueError, p, 1, None)

    def test_function(self):
        p = FunctionGenerator(fungen, matcher = self.matcher)
        self.assertTrue(p.priority == 0)
        self.assertTrue(p.parent == None)
        self.assertTrue(p.match(0))
        self.assertFalse(p.match(1))
        self.check(p, 0, 'fungen 0\n')
        self.assertRaises(ValueError, p, 1, None)

    def test_template(self):
        tpl = TemplateMockup()
        p = TemplateGenerator(tpl, lambda x: x, matcher = self.matcher)
        self.assertTrue(p.priority == 0)
        self.assertTrue(p.parent == None)
        self.assertTrue(p.match(0))
        self.assertFalse(p.match(1))
        self.check(p, 0, 'template 0')
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

        self.check(p, 0, 'SimpleGenerator 0\n')
        self.check(p, 1, 'SimpleGenerator 1\n')
        self.check(p, 2, 'SimpleGenerator 2\n')
        self.assertRaises(ValueError, p, 4, None)

    def test_object_generator(self):
        p = MyObjectGenerator()
        self.assertTrue(p.priority == 0)
        self.assertTrue(p.parent == None)

        self.assertTrue(p.match(0))
        self.assertTrue(p.match(1))
        self.assertTrue(p.match(2))
        self.assertFalse(p.match(3))

        self.check(p, 0, 'FunctionSubgenerator 0\n')
        self.check(p, 1, 'Hello testrunner!! source = 1\n')
        self.check(p, 2, 'template testrunner! source = 2')
        self.assertRaises(ValueError, p, 4, None)
