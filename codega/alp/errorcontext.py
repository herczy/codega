class ErrorContext(object):
    '''Contains error(s) and warning(s) encountered during a
    parsing and lexing task.'''

    _error_list = None
    _warning_list = None

    def __init__(self):
        self._error_list = []
        self._warning_list = []

    def error(self, message, location):
        '''Emit an error message with a location information.'''

        self._error_list.append((message, location))

    def warning(self, message, location):
        '''Emit a warning message with a location information.'''

        self._warning_list.append((message, location))

    @property
    def errors(self):
        '''Count of error messages.'''

        return len(self._error_list)

    @property
    def warnings(self):
        '''Count of warning messages.'''

        return len(self._warning_list)

    @property
    def result(self):
        '''True if there were no errors.'''

        return len(self._error_list) == 0

    @property
    def summary(self):
        '''Summarize the errors and warnings.'''

        summary_line = '  %d error(s), %d warning(s)' % (self.errors, self.warnings)
        if not self._error_list and not self._warning_list:
            return summary_line

        res = []
        res.extend('%s: %s' % (loc, msg) for msg, loc in self._error_list)
        res.extend('%s: %s' % (loc, msg) for msg, loc in self._warning_list)
        return '%s\n\n%s' % ('\n'.join(res), summary_line)
