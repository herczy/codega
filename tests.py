from unittest import TestLoader, TextTestRunner

import tests

suites = TestLoader().loadTestsFromModule(tests)
TextTestRunner(verbosity = 2).run(suites)
