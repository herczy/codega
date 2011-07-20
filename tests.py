import os, os.path
import sys

from unittest import *

mypath = os.path.abspath(os.path.dirname(__file__))
testdir = os.path.join(mypath, 'tests')
exampledir = os.path.join(mypath, 'examples')

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

print >>sys.stderr, 'Running examples'
for f in os.listdir(exampledir):
    abspath = os.path.join(exampledir, f)

    if not os.path.isdir(abspath):
        continue

    print >>sys.stderr, 'Running example %s' % f

    cur = os.getcwd()
    try:
        os.chdir(os.path.join(exampledir, f))
        os.system('../../cgmake -f -d')

    finally:
        os.chdir(cur)
