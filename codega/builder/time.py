'''
Build tasks handle the building of a target.
'''

import os.path
import stat

def get_mtime(filename):
    '''Get the modification time of a file'''

    if os.path.exists(filename):
        return os.stat(filename)[stat.ST_MTIME]

    return 0

def get_module_time(locator, module):
    '''Get the modification time for a module'''

    mod = locator.import_module(module)
    dirname, basename = os.path.split(mod.__file__)

    if os.path.splitext(basename)[0] != '__init__':
        return get_mtime(mod.__file__)

    res = []
    for root, dirs, files in os.walk(dirname):
        res.extend((get_mtime(os.path.join(root, f)) for f in files))

    return max(res)
