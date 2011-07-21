from unittest import TestCase, TestSuite
import os
import os.path
import tempfile

class TestExamples(TestCase):
    pass

def add_example_test(name, path):
    def __run(self):
        fd, fn = tempfile.mkstemp()

        cur = os.getcwd()
        try:
            os.chdir(os.path.join(exampledir, f))
            os.system('../../cgmake -d -f 2>%s' % fn)

        finally:
            os.chdir(cur)

        data = os.read(fd, 100000)
        self.assertNotEqual(data[:7], 'Error: ')

    setattr(TestExamples, 'test_example_%s' % name, __run)

mypath = os.path.abspath(os.path.dirname(__file__))
exampledir = os.path.join(os.path.dirname(mypath), 'examples')

for f in os.listdir(exampledir):
    abspath = os.path.join(exampledir, f)

    if not os.path.isdir(abspath):
        continue

    add_example_test(f, abspath)
