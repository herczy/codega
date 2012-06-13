from unittest import TestCase

from codega.utils.decorators import *

@mark('mark0', 0)
@mark('mark1', 1)
@mark('mark2', 2)
def marked():
    pass

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

class TestDecorators(TestCase):
    def test_abstract(self):
        @abstract
        def abstract_function(self):
            pass

        self.assertRaises(NotImplementedError, abstract_function, None)

    def test_set_mark(self):
        def x():
            pass

        set_mark(x, 'mark', 1)
        self.assertTrue(has_mark(x, 'mark'))
        self.assertEqual(get_mark(x, 'mark'), 1)

    def test_marks(self):
        self.assertEqual(get_mark(marked, 'mark0'), 0)
        self.assertEqual(get_mark(marked, 'mark1'), 1)
        self.assertEqual(get_mark(marked, 'mark2'), 2)
        self.assertRaises(AttributeError, get_mark, marked, 'mark3')
        self.assertEqual(get_mark_default(marked, 'mark3', default= -1), -1)

        self.assertTrue(has_mark(marked, 'mark0'))
        self.assertTrue(has_mark(marked, 'mark1'))
        self.assertTrue(has_mark(marked, 'mark2'))
        self.assertFalse(has_mark(marked, 'mark3'))

    def test_copy_mark(self):
        global marked

        @mark('mark5', 3)
        def __marked_copy(self):
            pass

        copy_marks(__marked_copy, marked)
        old = marked
        try:
            marked = __marked_copy
            self.test_marks()

            self.assertTrue(has_mark(marked, 'mark5'))
            self.assertTrue(get_mark(marked, 'mark5'), 3)

        finally:
            marked = old

        self.assertFalse(has_mark(marked, 'mark5'))

    def test_collect_marked_object(self):
        obj = TestObject()
        self.assertEqual(set(collect_marked_bound(obj, 'mark0')), set([(0, obj.marked_0), (1, obj.marked_1), (2, obj.marked_2), (0, obj.marked_3), ]))
        self.assertEqual(set(collect_marked_bound(obj, 'mark0', 0)), set([(0, obj.marked_0), (0, obj.marked_3), ]))
        self.assertEqual(set(collect_marked_bound(obj, 'mark1')), set([(0, obj.marked_4), ]))
