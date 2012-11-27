from unittest import TestCase

from codega.visitor import *


class ExampleVisitor(VisitorBase):
    def aspects(self, node):
        return [node, -node]

    @visitor(1)
    def visit_0(self, num):
        return abs(num)


class TestVisitor(TestCase):
    def setUp(self):
        self._visitor = ExampleVisitor()

    def test_base_metaattr(self):
        self.assertEquals(self._visitor.__visitors__, { 1: ExampleVisitor.visit_0.im_func })

    def test_base_aspect(self):
        self.assertEquals(self._visitor.aspects(1), [1, -1])

    def test_base_visit(self):
        self.assertEquals(self._visitor.visit(-1), 1)

    def test_base_fallback(self):
        self.assertEquals(self._visitor.visit(-2), None)

    def test_class_aspects(self):
        self.assertEquals(ClassVisitor().aspects(ExampleVisitor()), ExampleVisitor.__mro__)

    def test_xml_aspect(self):
        t = type('test', (object,), dict(tag='testtag'))()
        self.assertEquals(XmlVisitor().aspects(t), ['testtag'])

    def test_explicit_aspect(self):
        self.assertEquals(ExplicitVisitor().aspects(1), [1])
