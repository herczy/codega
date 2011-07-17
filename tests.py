import os, os.path
import sys

from unittest import *

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
