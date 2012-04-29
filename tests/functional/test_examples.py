from unittest import TestCase
import os.path
import sys

from tests.common import make_tempfile

class TestExamples(TestCase):
    pass

def add_example_test(name, path):
    def __run(self):
        with make_tempfile() as (fd, fn):
            cur = os.getcwd()
            try:
                os.chdir(os.path.join(exampledir, name))
                rc = os.system('../../cgx make -f -v debug 2>%s' % fn)

                if rc == 0:
                    rc = os.system('../../cgx clean -v debug 2>>%s' % fn)

            finally:
                os.chdir(cur)

            if rc != 0:
                print >> sys.stderr, "stderr output from 'cgx build -f'"
                sys.stderr.write(open(fn, 'r').read())

            self.assertEqual(rc, 0)

    setattr(TestExamples, 'test_example_%s' % name, __run)

mypath = os.path.abspath(os.path.dirname(__file__))
exampledir = os.path.join(os.path.dirname(mypath), '..', 'examples')

for f in os.listdir(exampledir):
    abspath = os.path.join(exampledir, f)

    if not os.path.isdir(abspath):
        continue

    if not os.path.isfile(os.path.join(abspath, 'codega.xml')) and not os.path.isfile(os.path.join(abspath, 'codega')):
        continue

    add_example_test(f, abspath)
