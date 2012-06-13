from unittest import TestCase

from codega.utils.ordereddict import OrderedDict

class TestOrderedDict(TestCase):
    def test_ordering(self):
        '''The proper order is kept when adding items to an ordered dict.'''

        od = OrderedDict()
        keys = [ 'a', 'A', 'b', 'B', 'c', 'C' ] + range(100) + range(500, 400, -1)
        for i in keys:
            od[i] = '--%r' % i

        for index, key in zip(od.keys(), keys):
            self.assertEqual(index, key)

        # overwriting should not affect the order
        od['C'] = 1000

        for index, check in zip(od.keys(), keys):
            self.assertEqual(index, check)

        pos = len(od._keyorder)
        od['x'] = 1
        self.assertEqual(od._keyorder[pos], 'x')

    def test_item_access(self):
        '''The item access (get, set, delete) works as expected.'''

        od = OrderedDict()
        od[2] = 1
        od[1] = 2
        od['a'] = 3

        self.assertEqual(od[1], 2)
        self.assertEqual(od[2], 1)
        self.assertEqual(od['a'], 3)
        self.assertEqual(od.keys(), [2, 1, 'a'])

        del od[1]
        self.assertEqual(od[2], 1)
        self.assertEqual(od['a'], 3)
        self.assertEqual(od.keys(), [2, 'a'])

    def test_insert(self):
        '''The insert operation on an ordered dict works properly.'''

        od = OrderedDict()
        for i in range(10):
            od[i] = 100 * i

        # New item
        od.insert(0, -1, 0)
        self.assertEqual(od.keys(), [-1] + range(10))
        od._keyorder = range(10)

        # Reordering
        #  a., insert before the old position
        od.insert(0, 5, 0)
        self.assertEqual(od.keys(), [5] + range(5) + range(6, 10))
        od._keyorder = range(10)

        #  b., insert after the old position
        od.insert(7, 5, 0)
        self.assertEqual(od.keys(), range(5) + [6, 5, 7, 8, 9])
        od._keyorder = range(10)

    def test_update(self):
        '''The update operation works on an ordered dict properly.'''

        od1 = OrderedDict()
        for i in range(10):
            od1[i] = 100 * i

        keys1 = od1.keys()

        od2 = OrderedDict()
        for i in range(10, 20):
            od2[i] = 100 * i

        od1.update(od2)
        for index, check in zip(od1.keys(), range(20)):
            self.assertEqual(index, check)

        od1._keyorder = keys1

        od1.update(0, od2)
        for index, check in zip(od1.keys(), range(10, 20) + range(10)):
            self.assertEqual(index, check)

        self.assertRaises(TypeError, od1.update, 0, od1, 1)

    def test_index(self):
        '''The index of the key can be queried.'''

        od = OrderedDict()
        od['a'] = 2
        od[None] = 2
        od[1] = 2

        self.assertEqual(od.index('a'), 0)
        self.assertEqual(od.index(None), 1)
        self.assertEqual(od.index(1), 2)
