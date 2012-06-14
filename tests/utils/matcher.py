from unittest import TestCase
from lxml import etree

from codega.utils.matcher import *

class TestMatcherBase(TestCase):
    def test_abstract_call(self):
        '''MatcherBase.__call__ is abstract.'''

        self.assertRaises(NotImplementedError, MatcherBase().__call__, 0, 0)

    def test_neg(self):
        '''Negation of a matcher works.'''

        class MyMatcher(MatcherBase):
            def __call__(self, source, context):
                return source and context

        matcher = MyMatcher()

        self.assertEqual(matcher(0, 0), False)
        self.assertEqual(matcher(1, 0), False)
        self.assertEqual(matcher(1, 1), True)

        self.assertEqual(matcher.neg(0, 0), True)
        self.assertEqual(matcher.neg(1, 0), True)
        self.assertEqual(matcher.neg(1, 1), False)

class TestFunctionMatcher(TestCase):
    def test_match(self):
        '''Function matcher works properly.'''

        def func(source, context):
            return source and context

        matcher = FunctionMatcher(func)
        self.assertEqual(matcher(0, 0), False)
        self.assertEqual(matcher(1, 0), False)
        self.assertEqual(matcher(1, 1), True)

        self.assertEqual(matcher.neg(0, 0), True)
        self.assertEqual(matcher.neg(1, 0), True)
        self.assertEqual(matcher.neg(1, 1), False)

    def test_matcher_decorator(self):
        '''Function matcher decorator is just an alias to the class.'''

        self.assertEqual(matcher, FunctionMatcher)

class TestCombinedMatcher(TestCase):
    def test_combine(self):
        '''CombineMatcher works properly.'''

        def op(*args):
            return bool(sum(args))

        @matcher
        def match0(source, context):
            return source

        @matcher
        def match1(source, context):
            return context

        comb = CombinedMatcher(op, match0, match1)
        self.assertEqual(comb(0, 0), False)
        self.assertEqual(comb(1, 0), True)
        self.assertEqual(comb(-3, 3), False)

        self.assertEqual(comb.neg(0, 0), True)
        self.assertEqual(comb.neg(1, 0), False)
        self.assertEqual(comb.neg(-3, 3), True)

class TestMatcherFunctions(TestCase):
    cls0 = type('cls0', (object,), dict(a=0, b=1))
    cls1 = type('cls1', (object,), dict(a=0, b=1))

    _data_set = {
      'FF' : (False, False),
      'FT' : (False, True),
      'TF' : (True, False),
      'TT' : (True, True),
      'xml' : (etree.Element('xmltag', attrib=dict(a0='a0', a1='a1'), text='hello'), None),
      'xml2' : (etree.Element('xmltag2', attrib=dict(a0='a0', a1='a1'), text='hello'), None),
      'comment' : (etree.Comment('AAAA'), None),
      'cls0' : (cls0(), None),
      'cls1' : (cls1(), None),
    }

    child = etree.Element('child')
    node = etree.Element('parent')
    node.append(child)
    _data_set['xmlparent'] = (node, None)
    _data_set['xmlchild'] = (child, None)

    def map_matcher(self, matcher_obj, **results):
        for key, (source, context) in self._data_set.items():
            if key in results:
                self.assertEqual(matcher_obj(source, context), results[key], msg='Failure; matcher=%r, key=%r, source=%r, context=%r' % (matcher_obj, key, source, context))

            else:
                # Just run the matcher to weed out unhandled exceptions
                matcher_obj(source, context)

    def test_always(self):
        '''Always matcher returns true every time.'''

        self.map_matcher(always, FF=True, FT=True, TF=True, TT=True)

    def test_never(self):
        '''Never matcher returns false every time.'''

        self.map_matcher(never, FF=False, FT=False, TF=False, TT=False)

    def test_comment(self):
        '''Comment matcher returns true on XML Etree comment nodes.'''

        self.map_matcher(comment, xml=False, comment=True, FF=False)

    def test_tag(self):
        '''Tag matcher returns true on XML Etree nodes with the specified tag.'''

        self.map_matcher(tag('xmltag'), xml=True, xml2=False, comment=False, FF=False)

    def test_parent(self):
        '''Parent matcher returns true on XML Etree nodes with the specified parent tag.'''

        self.map_matcher(parent('parent'), xmlchild=True, xmlparent=False, comment=False, xml=False, xml2=False, FF=False)
        self.map_matcher(root, xmlchild=False, xmlparent=True, xml=True, comment=True, FF=False)

    def test_xpath(self):
        '''XPath matcher returns true when the XML Etree node path matches.'''

        self.map_matcher(xpath('parent'), parent=True, child=False)
        self.map_matcher(xpath('parent/child'), parent=False, child=True)
        self.map_matcher(xpath('parent/*'), parent=False, child=True)

    def test_cls(self):
        '''Class matcher returns true when the class is matched.'''

        self.map_matcher(cls(self.cls0), cls0=True, cls1=False)

    def test_any(self):
        '''If any of the matchers match, the aggregate will too.'''

        self.map_matcher(any(always, never), FF=True, FT=True, TF=True, xml=True)

    def test_all(self):
        '''If any of the matchers fail to match, the aggregate will too.'''

        self.map_matcher(all(always, never), FF=False, FT=False, TF=False, xml=False)
