import tempfile
from ply import yacc

from codega.decorators import abstract

from tools import replace, cleanup_file_list
import logger
from codega.alp.location import LocationRange


class ParserBase(object):
    '''Base class for yacc parsers.'''

    lexer_object = None
    parser_object = None

    error_message = 'Invalid token: @token@'

    def __init__(self, lexer):
        self.lexer_object = lexer

        # Create logger for parser
        self.log = logger.getLogger('parser-%d' % logger.sysid(self))

        # The temporary parsetab.py file should be generated in /tmp.
        parse_tab = tempfile.NamedTemporaryFile(prefix='parsetab-')
        # This is a hack, since ply appends a .py to the supplied tabmodule name.
        # So not only do we create a file for nothing but if not cleaned up manually
        # a tempfile will be leaked. Thanks, David Beazley. ;-)
        cleanup_file_list.append(parse_tab.name + '.py')

        # Create ply parser
        log_wrapper = logger.PlyLoggerWrapping(self.log)
        self.parser_object = yacc.yacc(module=self, debuglog=log_wrapper, errorlog=log_wrapper, debug=1, tabmodule=parse_tab.name)

        self.log.info('Created parser; class ID=%d' % logger.sysid(self.__class__))

    def p_error(self, token):
        if token is not None:
            self.lexer_object.error_context.error(replace(self.error_message, token=token.value, type=token.type), token.location)
            self.log.error('Invalid token; value=%s, type=%s, location=%s' % (token.value, token.type, token.location))

        else:
            self.lexer_object.error_context.error("Unexpected end of file", self.lexer_object.current_location)
            self.log.error('Unexpected end of file')

    def parse(self):
        with logger.Progress('Input parsing', self.log.info) as process:
            res = self.parser_object.parse(lexer=self.lexer_object, tracking=True)

            if res is None:
                process.fail()

            return res

    def input(self, data):
        self.lexer_object.input(data)
        self.log.debug('Parser got input; length=%d' % len(data))

    def token(self):
        token = self.lexer_object.token()
        if token is None:
            self.last_token_location = None
            self.log.debug('End of input reached')

        else:
            self.last_token_location = token.location
            self.log.debug('Got next token; value=%r, type=%s, location=%s' % (token.value, token.type, token.location))

        return token

    def get_location(self, prod):
        start, end = (self.lexer_object.get_location(pos) for pos in prod.lexspan(0))
        return LocationRange(start, end)

    def report_error(self, *args, **kwargs):
        self.__report(self.lexer_object.error_context.error, *args, **kwargs)

    def report_warning(self, *args, **kwargs):
        self.__report(self.lexer_object.error_context.warning, *args, **kwargs)

    @property
    def tokens(self):
        return self.lexer_object.tokens

    @abstract
    def handle_error(self):
        pass

    @classmethod
    def subclass(cls, name, members, metacls=type):
        return metacls(name, (cls,), members)

    def __report(self, func, msg, rule, prod, location=None):
        args = dict(('prod%d' % (i + 1), repr(entry)) for i, entry in enumerate(prod[1:]))
        args['rule'] = repr(rule)
        args['start'] = location.start
        args['end'] = location.end
        args['location'] = location

        exp = replace(msg, **args)
        func(exp, location)
