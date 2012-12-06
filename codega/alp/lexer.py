import re

from ply import lex
from ply.lex import TOKEN

from location import Location
from errorcontext import ErrorContext
from tools import replace
import logger

keyword_regex = re.compile('^[a-zA-Z_][a-zA-Z0-9_]*$')


class Lexer(object):
    '''Custom, ply-based lexer. Takes the tokens the same way the ply
    lexer takes but makes some extra additional comfort features.'''

    source_name = None
    error_context = None
    lexer_object = None
    current_location = None

    error_tokens = None
    warning_tokens = None

    error_message = 'Invalid token: @token@'

    token_list = None

    def __init__(self, source_name, error_context):
        self.source_name = source_name
        self.error_context = error_context
        self.current_location = Location(self.source_name, 0, 0, 0)
        self.data = ''

        # Create logger for lexer
        self.log = logger.getLogger('lexer-%d' % logger.sysid(self))

        # Create ply lexer object
        log_wrapper = logger.PlyLoggerWrapping(self.log)
        self.lexer_object = lex.lex(module=self, debuglog=log_wrapper, errorlog=log_wrapper, debug=1)

        self.log.info('Created lexer; class ID=lexer-class-%d' % logger.sysid(self.__class__))

    @property
    def lineno(self):
        if self.lexer_object is None:
            return None

        return self.lexer_object.lineno

    @property
    def lexpos(self):
        if self.lexer_object is None:
            return None

        return self.lexer_object.lexpos

    def get_location(self, position):
        loc = Location(self.source_name, 0, 0, 0)
        loc.update(self.data[:position])

        return loc

    def input(self, data):
        self.data = data
        self.lexer_object.input(data)
        self.log.debug('Lexer got input; length=%d' % len(data))

    def token(self):
        prev_pos = self.lexer_object.lexpos

        token = self.lexer_object.token()
        if token is not None:
            token.location = self.current_location.clone()
            self.log.debug('Got next token; value=%r, type=%s, location=%s' % (token.value, token.type, token.location))

        else:
            self.log.debug('End of file reached; location=%s' % self.current_location)

        data = self.lexer_object.lexdata[prev_pos:self.lexer_object.lexpos]
        self.current_location.update(data)

        if token is not None:
            if token.type in self.error_tokens:
                error = replace(self.error_tokens[token.type], type=token.type, value=token.value, location=token.location)
                self.error_context.error(error, token.location)
                self.log.error(error)
                return None

            if token.type in self.warning_tokens:
                warning = replace(self.warning_tokens[token.type], type=token.type, value=token.value, location=token.location)
                self.error_context.warning(warning, token.location)
                self.log.warning(warning)

        return token

    def ignore_token(self, token):
        self.log.debug('Ignoring token; value=%r, type=%s, location=%s' % (token.value, token.type, self.current_location))

    @property
    def tokens(self):
        return self.token_list

    def t_error(self, t):
        token = t.value[0]
        self.error_context.error(replace(self.error_message, token=token), self.current_location.clone())

        self.lexer_object.skip(len(token))
        self.log.error('Error parsing character %r' % token)


class LexerFactory(object):
    '''Create a Lexer object with the given settings.'''

    _tokens = None
    _literals = None
    _ignored = None

    _error_context = None
    _error_message = None

    def __init__(self):
        self._tokens = {}
        self._literals = set()
        self._ignored = set()

        self._error_tokens = {}
        self._warning_tokens = {}

        self.log = logger.getLogger('lexer-factory-%d' % logger.sysid(self))
        self.log.info('Initialized lexer factory')

    def add_token(self, name, regexp, error=None, warning=None):
        '''Add a list of tokens to parse.'''

        self._tokens[name] = regexp
        if error is not None:
            self._error_tokens[name] = error

        elif warning is not None:
            self._warning_tokens[name] = warning

        self.log.debug('Added token type %s; regex=%r' % (name, regexp))

    def add_ignore_token(self, name, *args, **kwargs):
        '''Add a list of tokens to be ignored.'''

        self._ignored.add(name)
        self.add_token(name, *args, **kwargs)
        self.log.debug('Added ignored token(s)')

    def add_literal(self, name, value, *args, **kwargs):
        '''Add literal tokens. Literal tokens are escaped before being added.'''

        self._literals.add(name)
        self.add_token(name, value, *args, **kwargs)
        self.log.debug('Added literal(s)')

    def add_keyword(self, keyword):
        '''Add keywords. Keywords are tokens where the
        type is the uppercase of the keyword'''

        if not keyword_regex.match(keyword):
            raise ValueError("Keyword %r invalid", keyword)

        self.add_literal(keyword.upper(), keyword)
        self.log.debug("Added keyword token %s" % keyword)

    def set_error_context(self, context, message=None):
        '''Set error context with an error message template.'''

        self._error_context = context
        self._error_message = message
        self.log.debug("Set error context and message; context ID=%d, message=%r" % (logger.sysid(context), message))

    def __make_lex_member(self, expression, literal_state, action=None):
        '''Make a tokenizer function or string.'''

        matches = {}

        regex = re.compile(expression)
        for key in literal_state:
            literal = self._tokens[key]
            if regex.match(literal):
                matches[literal] = key

                self.log.debug("Literal %r was matched by %r" % (literal, expression))

        if not matches:
            self.log.debug("No literals matched by token %r" % expression)

            if action is None:
                action = expression

            return literal_state, action

        if action is None:

            @TOKEN(expression)
            def tokenizer(self, t):
                if t.value in matches:
                    t.type = matches[t.value]
                    return t

                return t

        else:

            @TOKEN(expression)
            def tokenizer(self, t):
                if t.value in matches:
                    t.type = matches[t.value]
                    return t

                return action(self, t)

        for delkey in matches.values():
            literal_state.remove(delkey)

        return literal_state, tokenizer

    def create_class(self):
        '''Dynamically create a new lexer class.'''

        cls_dict = {}
        literal = set(self._literals)
        for key, value in self._tokens.items():
            self.log.debug("Binding token %s(%r); remaining literals: %s" % (key, value, ', '.join(literal)))

            if key in literal:
                # The fate of how literals are handled depends whether
                # any other rule matches the given literal
                continue

            if key in self._ignored:
                name = 't_ignored_%s' % key
                action = lex.TOKEN(value)(lambda self, token: self.ignore_token(token))

            else:
                name = 't_%s' % key
                action = None

            literal, action = self.__make_lex_member(value, literal, action=action)
            cls_dict[name] = action

        for key in literal:
            self.log.debug("Binding remaining literal token %s" % key)

            cls_dict['t_%s' % key] = re.escape(self._tokens[key])

        if self._error_message is not None:
            cls_dict['error_message'] = self._error_message

        cls_dict['token_list'] = filter(lambda key: key not in self._ignored, self._tokens.keys())

        cls_dict['error_tokens'] = self._error_tokens
        cls_dict['warning_tokens'] = self._warning_tokens

        lexer_class = type('AutoLexer', (Lexer,), cls_dict)

        self.log.debug('Created lexer class; class ID=lexer-class-%d' % logger.sysid(lexer_class))
        return lexer_class

    def create(self, source_name):
        '''Create the new Lexer object.'''

        error_context = self._error_context or ErrorContext()
        cls = self.create_class()
        instance = cls(source_name, error_context)

        self.log.debug('Created lexer class; id=lexer-%d, context ID=%d' % (logger.sysid(instance), logger.sysid(error_context)))
        return instance
