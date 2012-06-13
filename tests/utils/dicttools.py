from unittest import TestCase

from codega.utils.dicttools import *

class TestDicttools(TestCase):
    def test_dict_from_element(self):
        '''Etree element attributes can be turned to dicts possibly with a base.'''

        base = dict(a=1, b=2)
        xml = type('xml', (object,), dict(attrib=dict(c=3, d=4, a=5)))

        # Dict from element without base
        self.assertEqual(dict_from_element(xml), xml.attrib)

        # Dict from element with base
        self.assertEqual(dict_from_element(xml, base), dict(a=5, b=2, c=3, d=4))

    def test_map_keys(self):
        '''Keys in dictionaries can be remapped with a function.'''

        base = {1:1, 2:2, 3:3}
        mapped = map_keys(str, base)
        self.assertEqual(mapped, {'1':1, '2':2, '3':3})

    def test_map_values(self):
        '''Values in dictionaries can be remapped with a function.'''

        base = {1:1, 2:2, 3:3}
        mapped = map_values(str, base)
        self.assertEqual(mapped, {1:'1', 2:'2', 3:'3'})

    def test_filter_by_keys(self):
        '''Dictionaries can be filtered by its keys.'''

        base = {1:1, 2:2, 3:3}
        self.assertEqual(filter_by_keys(lambda x: x == 2, base), {2:2})

    def test_filter_keys(self):
        '''Dictionaries can be filtered by sets.'''

        base = {1:1, 2:2, 3:3}
        self.assertEqual(filter_keys(base, (2,)), {2:2})

    def test_exclude_internals(self):
        '''Internal keywords can be filtered from dictionaries.'''

        base = dict(a=1, __base__=2, self=3)
        self.assertEqual(exclude_internals(base), dict(a=1))

    def test_bindict(self):
        '''Using an XML element and other bindings a dictionary can be created with some auto elements.'''

        xml = type('xml', (object,), dict(attrib=dict(c=3, d=4, a=5)))
        bound = bindict(xml, 123, a=1, b=2, c=10, self=1234, __aaa__=7)
        self.assertEqual(bound, dict(arg_context=123, arg_source=xml, attr_c=3, attr_d=4, attr_a=5, a=1, b=2, c=10))

    def test_autobindict(self):
        '''Using an XML element and other bindings a dictionary can be created with some auto elements when calling a generator function.'''

        @autobindict
        def withret(self, source, context, bindings):
            return dict(a=1, self=1, __a__=1)

        @autobindict
        def withoutret(self, source, context, bindings):
            pass

        @autobindict
        def withoutretmodify(self, source, context, bindings):
            bindings['x'] = 2

        xml = type('xml', (object,), dict(attrib=dict(c=3, d=4, a=5)))
        self.assertEqual(withret(None, xml, 123), dict(arg_context=123, arg_source=xml, attr_c=3, attr_d=4, attr_a=5, a=1))
        self.assertEqual(withoutret(None, xml, 123), dict(arg_context=123, arg_source=xml, attr_c=3, attr_d=4, attr_a=5))
        self.assertEqual(withoutretmodify(None, xml, 123), dict(arg_context=123, arg_source=xml, attr_c=3, attr_d=4, attr_a=5, x=2))
