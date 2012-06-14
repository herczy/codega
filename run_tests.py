import os.path
import sys

from unittest import TestLoader, TestSuite, TextTestRunner

if __name__ == '__main__':
    import tests

    loader = TestLoader()
    suite = TestSuite()

    if len(sys.argv) == 1:
        suite.addTests(loader.loadTestsFromModule(tests))

    else:
        for mod in sys.argv[1:]:
            suite.addTests(loader.loadTestsFromModule(__import__(mod, fromlist=['*'])))

    TextTestRunner(verbosity=2).run(suite)
