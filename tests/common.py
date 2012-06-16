'''
Common unit test tools.
'''

import os
import tempfile

def make_tempfile(*args, **kwargs):
    class __section(object):
        def __enter__(self):
            self._fd, self._fn = tempfile.mkstemp(*args, **kwargs)
            return (self._fd, self._fn)

        def __exit__(self, *args, **kwargs):
            os.unlink(self._fn)

    return __section()

class RunInfo(object):
    def __init__(self, args, kwargs, result=None, exception=None):
        self.exception = exception
        self.args = args
        self.kwargs = kwargs
        self.result = result

    @property
    def success(self):
        return self.exception is not None

class MockMaker(object):
    def __init__(self, name=None, bases=(object,)):
        self._bases = bases
        self._name = name
        self._functions = {}
        self._attributes = {}

        if self._name is None:
            self._name = 'mock_class_%d' % id(self)

    def add_function(self, name, run=None, returns=None):
        self._functions[name] = (run, returns)

    def add_attribute(self, name, value=None, settable=True, gettable=True, deletable=True):
        self._attributes[name] = (value, settable, gettable, deletable)

    def create_mock_class(self):
        classdict = {}

        def increase_access(self, name):
            # Increase access count
            count = getattr(self, name + '_access_count')
            setattr(self, name + '_access_count', count + 1)

        def access_wrapper(name, func):
            def __wrapped(self, *args, **kwargs):
                increase_access(self, name)
                try:
                    result = func(*args, **kwargs)
                    setattr(self, name + '_lastrun', RunInfo(args, kwargs, result))

                except Exception, e:
                    setattr(self, name + '_lastrun', RunInfo(args, kwargs, exception=e))
                    raise

                return result

            return __wrapped

        def returner(result):
            return lambda self, *args, **kwargs: result

        def attribute(name, settable, gettable, deletable):
            propargs = dict()

            if settable:
                def setter(self, value):
                    increase_access(self, name)
                    setattr(self, name, value)

                propargs['fset'] = setter

            if gettable:
                def setter(self, value):
                    increase_access(self, name)
                    return getattr(self, name)

                propargs['fget'] = setter

            if deletable:
                def deleter(self, value):
                    increase_access(self, name)
                    delattr(self, name)

                propargs['fset'] = setter

            return property(**propargs)

        for name, (run, returns) in self._functions.items():
            classdict[name + '_access_count'] = 0
            classdict[name + '_lastrun'] = None

            if run is not None:
                classdict[name] = access_wrapper(name, run)

            else:
                classdict[name] = access_wrapper(name, returner(returns))

        for name, args in self._attributes.items():
            classdict[name + '_access_count'] = 0
            classdict[name] = attribute(name, *args)

        return type(self._name, self._bases, classdict)
