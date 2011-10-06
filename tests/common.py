'''
Common unit test tools.
'''

import os
import tempfile

def make_tempfile(*args, **kwargs):
    '''Return an object with the enter/exit mechanism to create temp files'''

    class __section(object):
        def __enter__(self):
            self._fd, self._fn = tempfile.mkstemp(*args, **kwargs)
            return (self._fd, self._fn)

        def __exit__(self, *args, **kwargs):
            os.unlink(self._fn)

    return __section()

def variant(name, *values):
    '''Specify a variant binding for a test case'''

    def __decorator(func):

        def __wrapper(*args, **kwargs):
            for value in values:
                kwargs[name] = value
                func(*args, **kwargs)

        return __wrapper

    return __decorator
