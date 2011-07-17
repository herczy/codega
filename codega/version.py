class Version(object):
    '''Version value type

    Members:
    _components -- Version components (1.0 becomes ['1', '0'])

    Static members:
    MAJOR_VERSION -- Index of major version component
    MINOR_VERSION -- Index of minor version component
    PATCH_VERSION -- Index of patch version component
    '''

    _components = None

    MAJOR_VERSION = 0
    MINOR_VERSION = 1
    PATCH_VERSION = 2

    def __init__(self, *components):
        try:
            self._components = map(int, components)

        except TypeError:
            raise TypeError("Version components can only be values convertable to ints")

    def __getitem__(self, index):
        '''Get version component.

        By default, if the component index is out of range, Version will return 0.

        Arguments:
        index -- Version component index
        '''

        if not isinstance(index, int) and not isinstance(index, long):
            raise KeyError("Index %r is not an integer" % index)

        if index < 0 or index >= len(self._components):
            return 0

        return self._components[index]

    def __len__(self):
        '''Returns number of components'''

        return len(self._components)

    def __cmp__(self, other):
        '''Compare two version objects

        Arguments:
        other -- Other version object
        '''

        check_length = max((len(self), len(other)))
        for index in range(check_length):
            res = self[index] - other[index]
            if res != 0:
                return -1 if res < 0 else 1

        return 0

    @classmethod
    def load_from_string(self, string):
        '''Parse version information from a string.

        Note that this can be extended to parse strings in different ways but here we'll be using
        this simple method until a different, more complex version parser is needed.

        Arguments:
        string -- Version string
        '''

        return Version(*map(lambda s: s if s else '0', string.split('.')))

    def __str__(self):
        '''Get version string'''

        return '.'.join(map(str, self._components))

    def __repr__(self):
        '''Get version representation'''

        return 'Version(%s)' % self
