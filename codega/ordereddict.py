from UserDict import DictMixin


class OrderedDict(object, DictMixin):
    '''Implements an ordered dictionary.

    The keys are always in the order they were added (or explicitly specified)

    Members:
    _data -- The wrapped dictionary
    _keyorder -- A list containing the key order
    '''

    _data = None
    _keyorder = None

    def __init__(self, iterable=()):
        self._data = {}
        self._keyorder = []

        if isinstance(iterable, dict):
            self._data = iterable.copy()
            self._keyorder = list(iterable.keys())

        elif isinstance(iterable, OrderedDict):
            self._data = iterable._data.copy()
            self._keyorder = list(iterable._keyorder)

        else:
            for key, value in iterable:
                self._keyorder.append(key)
                self._data[key] = value

    def keys(self):
        return list(self._keyorder)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        if key in self._data:
            self._data[key] = value

        else:
            self._keyorder.append(key)
            self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]
        self._keyorder.remove(key)

    def insert(self, pos, key, value):
        '''Insert a key at the specified position'''

        if key in self._keyorder:
            oldpos = self._keyorder.index(key)
            del self._keyorder[oldpos]

            if pos <= oldpos:
                self._keyorder.insert(pos, key)

            else:
                self._keyorder.insert(pos - 1, key)

        else:
            self._keyorder.insert(pos, key)

        self._data[key] = value

    def update(self, *args):
        if len(args) == 1:
            DictMixin.update(self, args[0])

        elif len(args) == 2:
            pos, udict = args

            for ndx, key in enumerate(udict.keys()):
                self.insert(pos + ndx, key, udict[key])

        else:
            raise TypeError("update expected at most 3 arguments, got " + repr(1 + len(args)))

    def index(self, key):
        return self._keyorder.index(key)
