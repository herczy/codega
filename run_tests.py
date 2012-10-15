from unittest import TestLoader, TextTestRunner

if __name__ == '__main__':
    import tests
    suite = TestLoader().loadTestsFromModule(tests)
    TextTestRunner(verbosity=2).run(suite)
