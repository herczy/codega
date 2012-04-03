class Immutable(object):
    _initialized = False

    def __init__(self):
        self._initialized = True

    def __setattr__(self, key, value):
        if self._initialized:
            raise AttributeError("%s.%s not settable" % (self.__class__.__name__, key))

        return super(Immutable, self).__setattr__(key, value)

    def __delattr__(self, key, value):
        if self._initialized:
            raise AttributeError("%s.%s not deletable" % (self.__class__.__name__, key))

        return super(Immutable, self).__delattr__(key, value)
