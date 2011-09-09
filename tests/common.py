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
