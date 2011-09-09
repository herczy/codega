'''Basic logging facilities. Is a wrapper to the built-in logger'''

import traceback
import sys

from lxml.etree import use_global_python_log, PyErrorLog
from logging import debug, info, warning, error, critical, log, DEBUG, INFO, WARNING, ERROR, CRITICAL

def prepare():
    import logging

    levels = {
        'debug' : DEBUG,
        'info' : INFO,
        'warning' : WARNING,
        'error' : ERROR,
        'critical' : CRITICAL,
        '4' : DEBUG,
        '3' : INFO,
        '2' : WARNING,
        '1' : ERROR,
        '0' : CRITICAL,
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
            print >> sys.stderr, "Unknown log level %s" % opt
            exit(1)

        del sys.argv[ndx:ndx + 2]

    else:
        loglevel = ERROR

    logging.getLogger().setLevel(loglevel)
    use_global_python_log(PyErrorLog())


def exception(preface = None, level = DEBUG, short_desc = None, long_desc = None, level_trace = None, line_prefix = None):
    exc_type, exc_value, trace = sys.exc_info()

    if short_desc is None:
        short_desc = str(exc_value)

    if long_desc is None:
        long_desc = traceback.format_exc()

    if level_trace is None:
        level_trace = level

    if line_prefix is None:
        line_prefix = ''

    if preface is None:
        log(level, short_desc)

    else:
        log(level, "%s: %s", preface, short_desc)

    for line in long_desc.split('\n'):
        log(level_trace, "%s%s", line_prefix, line)
