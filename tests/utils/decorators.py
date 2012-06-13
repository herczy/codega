from unittest import TestCase

from codega.utils.decorators import *

class TestObject(object):
    @mark('mark0', 0)
    def marked_0(self):
        pass

    @mark('mark0', 1)
    def marked_1(self):
        pass

    @mark('mark0', 2)
    def marked_2(self):
        pass

    @mark('mark0', 0)
    def marked_3(self):
        pass

    @mark('mark1', 0)
    def marked_4(self):
        pass

    def unmarked(self):
        pass

    attribute = None

class TestDecorators(TestCase):
    def test_set_attribute(self):
        '''The set_attributes decorator sets the doc and name attributes properly.'''

        @set_attributes('myfunc', 'mydoc')
        def x():
            'aaaa'

            return 1234

        self.assertEqual(x.__name__, 'myfunc')
        self.assertEqual(x.__doc__, 'mydoc')
        self.assertEqual(x(), 1234)

    def test_copy_attributes(self):
        '''The copy_attributes decorator copies the doc and name attributes from the source function properly.'''

        def myfunc():
            '''mydoc'''

        @copy_attributes(myfunc)
        def myotherfunc():
            'aaaa'

            return 1234

        self.assertEqual(myotherfunc.__name__, 'myfunc')
        self.assertEqual(myotherfunc.__doc__, 'mydoc')
        self.assertEqual(myotherfunc(), 1234)

    def test_abstract(self):
        '''Functions decorated with the abstract decorator always throw an error when called'''

        @abstract
        def abstract_function(self):
            pass

        self.assertRaises(NotImplementedError, abstract_function, None)

    def test_init_mark(self):
        '''Marks can be properly initialized on a function.'''

        func = lambda: None

        init_mark(func)
        self.assertEqual(func.__marks__, {})

        func.__marks__['a'] = ('b',)
        init_mark(func)
        self.assertEqual(func.__marks__, {'a' : ('b',)})

    def test_set_mark(self):
        '''Marks can be set on a function.'''

        def x():
            pass

        set_mark(x, 'mark', 1)
        self.assertTrue(has_mark(x, 'mark'))
        self.assertEqual(get_mark(x, 'mark'), 1)

        self.assertRaises(RuntimeError, set_mark, x, 'mark', 2)

    def test_copy_mark(self):
        '''Marks can be copied from one function to another.'''

        def f0():
            pass
        f0.__marks__ = dict(a=1, b=2)

        def f1():
            pass
        copy_marks(f1, f0)

        self.assertEquals(f1.__marks__, dict(a=1, b=2))

    def test_mark(self):
        '''The mark decorator properly sets marks.'''

        @mark('a', 1)
        @mark('b', 2)
        def x():
            pass

        self.assertEqual(x.__marks__, dict(a=1, b=2))

    def test_has_mark(self):
        '''The presence of a mark can be requested.'''

        @mark('a', 1)
        def x():
            pass

        self.assertTrue(has_mark(x, 'a'))
        self.assertFalse(has_mark(x, 'b'))

    def test_get_mark(self):
        '''The value of a mark can be requested.'''

        @mark('a', 1)
        def x():
            pass

        self.assertEqual(get_mark(x, 'a'), 1)
        self.assertRaises(AttributeError, get_mark, x, 'b')

    def test_get_mark_default(self):
        '''The value of a mark can be requested (with fallback to default value).'''

        @mark('a', 1)
        def x():
            pass

        self.assertEqual(get_mark_default(x, 'a', 5), 1)
        self.assertEqual(get_mark_default(x, 'b', 5), 5)
        self.assertEqual(get_mark_default(x, 'b'), None)

    def test_collect_marked(self):
        '''Marked functions can be collected.'''

        m0 = (0, TestObject.__dict__.get('marked_0'))
        m1 = (1, TestObject.__dict__.get('marked_1'))
        m2 = (2, TestObject.__dict__.get('marked_2'))
        m3 = (0, TestObject.__dict__.get('marked_3'))

        # Test collecting by type
        expected = set([m0, m1, m2, m3])
        self.assertEqual(set(collect_marked(TestObject.__dict__, 'mark0')), expected)

        # Test collecting by type and value
        expected = set([m0, m3])
        self.assertEqual(set(collect_marked(TestObject.__dict__, 'mark0', 0)), expected)

    def test_collect_marked_bound(self):
        '''Marked functions can be collected.'''

        obj = TestObject()
        m0 = (0, getattr(obj, 'marked_0'))
        m1 = (1, getattr(obj, 'marked_1'))
        m2 = (2, getattr(obj, 'marked_2'))
        m3 = (0, getattr(obj, 'marked_3'))

        # Test collecting by type
        expected = set([m0, m1, m2, m3])
        self.assertEqual(set(collect_marked_bound(obj, 'mark0')), expected)

        # Test collecting by type and value
        expected = set([m0, m3])
        self.assertEqual(set(collect_marked_bound(obj, 'mark0', 0)), expected)
