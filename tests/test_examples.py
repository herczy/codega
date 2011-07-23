from unittest import TestCase, TestSuite
import os
import os.path
import sys
import tempfile

class TestExamples(TestCase):
    pass

def add_example_test(name, path):
    def __run(self):
        fd, fn = tempfile.mkstemp()

        cur = os.getcwd()
        try:
            os.chdir(os.path.join(exampledir, f))
            rc = os.system('../../cgx make -f 2>%s' % fn)

        finally:
            os.chdir(cur)

        if rc != 0:
            print >>sys.stderr, "stderr output from 'cgx build -f'"
            sys.stderr.write(open(fn, 'r').read())

        self.assertEqual(rc, 0)

    setattr(TestExamples, 'test_example_%s' % name, __run)

mypath = os.path.abspath(os.path.dirname(__file__))
exampledir = os.path.join(os.path.dirname(mypath), 'examples')

for f in os.listdir(exampledir):
    abspath = os.path.join(exampledir, f)

    if not os.path.isdir(abspath):
        continue

    add_example_test(f, abspath)
