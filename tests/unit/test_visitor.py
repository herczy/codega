from unittest import TestCase

from codega.visitor import *

class TestVisitorFunction(TestCase):
    def test_visitor_marking(self):
        @visitor('a', 'b')
        def test():
            pass

        from codega.decorators import has_mark, get_mark

        self.assertTrue(has_mark(test, 'visit'))
        self.assertEqual(get_mark(test, 'visit'), ('a', 'b'))
        self.assertEqual(test.__marks__.keys(), ['visit'])

class TestVisitorType(TestCase):
    def test_visitor(self):
        expected_visitors = dict()
        class TestVisitorClass(object):
            __metaclass__ = VisitorType

            @visitor('a')
            def x(self):
                pass

            expected_visitors['a'] = x

            @visitor('b', 'c')
            def y(self):
                pass

            expected_visitors['b'] = y
            expected_visitors['c'] = y

            def not_a_visitor(self):
                pass

        self.assertEqual(TestVisitorClass.__visitors__, expected_visitors)

    def test_visitor_collision(self):
        @visitor('a')
        def a(self):
            pass

        @visitor('a')
        def a2(self):
            pass

        members = dict(a=a, a2=a2)
        self.assertRaises(AttributeError, VisitorType, 'error', (object,), members)

class TestVisitorBase(TestCase):
    def test_aspects(self):
        self.assertRaises(NotImplementedError, VisitorBase().aspects)

    def test_visit(self):
        class Visitor(VisitorBase):
            def aspects(self, node):
                return [ node['aspect'] ]

            @visitor('a')
            def a(self, node):
                return 0

            @visitor('b', 'c')
            def b(self, node):
                return 1

            def visit_fallback(self, node):
                return 2

        self.assertEqual(Visitor().visit({'aspect' : 'a'}), 0)
        self.assertEqual(Visitor().visit({'aspect' : 'b'}), 1)
        self.assertEqual(Visitor().visit({'aspect' : 'c'}), 1)
        self.assertEqual(Visitor().visit({'aspect' : 'd'}), 2)
        self.assertEqual(Visitor().visit({'aspect' : 'xxxc'}), 2)

class TestClassVisitor(TestCase):
    def test_aspects(self):
        class A(object):
            pass

        class B(object):
            pass

        class AA(A):
            pass

        class BB(B):
            pass

        class AB(A, B):
            pass

        obj = ClassVisitor()
        self.assertEqual(obj.aspects(object()), (object, ))
        self.assertEqual(obj.aspects(A()), (A, object))
        self.assertEqual(obj.aspects(B()), (B, object))
        self.assertEqual(obj.aspects(AA()), (AA, A, object))
        self.assertEqual(obj.aspects(BB()), (BB, B, object))
        self.assertEqual(obj.aspects(AB()), (AB, A, B, object))

class TestXmlVisitor(TestCase):
    def test_aspects(self):
        class XmlMock(object):
            def __init__(self, tag):
                self.tag = tag

        self.assertEqual(XmlVisitor().aspects(XmlMock('a')), [ 'a' ])

class TestExplicitVisitor(TestCase):
    def test_aspects(self):
        self.assertEqual(ExplicitVisitor().aspects(0), [ 0 ])
