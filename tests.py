import os, os.path
import sys

from unittest import *

import __builtin__

runlist = list(sys.argv[1:])
mypath = os.path.abspath(os.path.dirname(__file__))
testdir = os.path.join(mypath, 'tests')

sys.path.insert(0, testdir)

loader = TestLoader()
suites = []

if runlist:
    files = map(lambda s: 'test_%s.py' % s, runlist)

else:
    files = list(os.listdir(testdir))

for f in files:
    modname, ext = os.path.splitext(f)

    if modname[:5] != 'test_':
        continue

    if ext != '.py':
        continue

    module = __import__(modname)
    suites.append(loader.loadTestsFromModule(module))

alltests = TestSuite(suites)
TextTestRunner(verbosity = 2).run(alltests)
