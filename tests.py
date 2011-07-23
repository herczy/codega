import os, os.path
import sys
import tempfile

from unittest import *

import __builtin__

__builtin__.__cleanup_list__ = []
def cleanup_file(filename):
    def __cleanup():
        os.unlink(filename)

    __cleanup_list__.append(__cleanup)

def make_tempfile(*args, **kwargs):
    fd, fn = tempfile.mkstemp(*args, **kwargs)
    cleanup_file(fn)
    return fd, fn
__builtin__.make_tempfile = make_tempfile

try:
    mypath = os.path.abspath(os.path.dirname(__file__))
    testdir = os.path.join(mypath, 'tests')

    sys.path.insert(0, testdir)

    loader = TestLoader()
    suites = []
    for f in os.listdir(testdir):
        modname, ext = os.path.splitext(f)

        if modname[:5] != 'test_':
            continue

        if ext != '.py':
            continue

        module = __import__(modname)
        suites.append(loader.loadTestsFromModule(module))

    alltests = TestSuite(suites)
    TextTestRunner(verbosity = 2).run(alltests)

finally:
    for fun in __cleanup_list__:
        fun()
