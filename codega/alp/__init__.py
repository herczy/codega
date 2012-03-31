import sys
import os.path
import types

from script import parse_file

class AlpLoader(object):
    def __init__(self, fullpath):
        self.fullpath = fullpath

    def load_module(self, name):
        return parse_file(self.fullpath, name)

class AlpFinder(object):
    def find_module(self, fullname, path=None):
        if path is None:
            find_in = sys.path

        else:
            find_in = path

        checkname = '%s.alp' % fullname.split('.')[-1]
        for base in find_in:
            fullpath = os.path.join(base, checkname)

            if os.path.isfile(fullpath):
                return AlpLoader(fullpath)

finder = AlpFinder()
def enable_loader():
    if finder not in sys.meta_path:
        sys.meta_path.append(finder)

def disable_loader():
    if finder in sys.meta_path:
        sys.meta_path.remove(finder)
