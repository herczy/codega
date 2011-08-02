'''Basic logging facilities. Is a wrapper to the built-in logger'''

from lxml.etree import use_global_python_log, PyErrorLog
from logging import debug, info, warning, error, critical, exception, log

def prepare():
    import logging
    import sys

    levels = {
        'debug' : logging.DEBUG,
        'info' : logging.INFO,
        'warning' : logging.WARNING,
        'error' : logging.ERROR,
        'critical' : logging.CRITICAL,
        '4' : logging.DEBUG,
        '3' : logging.INFO,
        '2' : logging.WARNING,
        '1' : logging.ERROR,
        '0' : logging.CRITICAL,
    }

    logging.basicConfig(format = '%(levelname) -10s %(message)s')

    for ndx, opt in enumerate(sys.argv):
        if opt == '-v' or opt == '--verbosity':
            break

    else:
        ndx = -1

    if ndx > 0:
        try:
            loglevel = levels[sys.argv[ndx + 1]]

        except KeyError:
            print >>sys.stderr, "Unknown log level %s" % opt
            exit(1)

        del sys.argv[ndx:ndx+2]

    else:
        loglevel = logging.ERROR

    logging.getLogger().setLevel(loglevel)
    use_global_python_log(PyErrorLog())
