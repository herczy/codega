from unittest import TestCase
import os.path
import sys

from common import make_tempfile

class TestExamples(TestCase):
    pass

def add_example_test(name, path):
    def __run(self):
        with make_tempfile() as (fd, fn):
            cur = os.getcwd()
            try:
                os.chdir(os.path.join(exampledir, name))
                rc = os.system('make LOGLEVEL=debug clean all >%s 2>&1' % fn)

                if rc == 0:
                    rc = os.system('make LOGLEVEL=debug clean >>%s 2>&1' % fn)

            finally:
                os.chdir(cur)

            if rc != 0:
                print >> sys.stderr, "stderr output from 'make'"
                sys.stderr.write(open(fn, 'r').read())

            self.assertEqual(rc, 0)

    __run.__doc__ = 'Running example %r in path %r' % (name, path)
    setattr(TestExamples, 'test_example_%s' % name, __run)

mypath = os.path.abspath(os.path.dirname(__file__))
exampledir = os.path.join(os.path.dirname(mypath), 'examples')

for f in os.listdir(exampledir):
    abspath = os.path.join(exampledir, f)

    if not os.path.isdir(abspath):
        continue

    if not os.path.isfile(os.path.join(abspath, 'Makefile')):
        continue

    add_example_test(f, abspath)
