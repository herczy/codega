import re

from ply import lex
from ply.lex import TOKEN

from location import Location
from errorcontext import ErrorContext
from tools import replace
import logger

keyword_regex = re.compile('^[a-zA-Z_][a-zA-Z0-9_]*$')

class Lexer(object):
    '''
    Custom, ply-based lexer. Takes the tokens the same way the ply
    lexer takes but makes some extra additional comfort features.
    '''

    source_name = None
    error_context = None
    lexer_object = None
    current_location = None

    error_message = 'Invalid token: @token@'

    token_list = None

    def __init__(self, source_name, error_context):
        self.source_name = source_name
        self.error_context = error_context
        self.current_location = Location(self.source_name, 0, 0, 0)

        # Create logger for lexer
        self.log = logger.getLogger('lexer-%d' % logger.sysid(self))

        # Create ply lexer object
        log_wrapper = logger.PlyLoggerWrapping(self.log)
        self.lexer_object = lex.lex(module=self, debuglog=log_wrapper, errorlog=log_wrapper, debug=1)

        self.log.info('Created lexer; class ID=lexer-class-%d' % logger.sysid(self.__class__))

    def input(self, data):
        self.lexer_object.input(data)
        self.log.debug('Lexer got input; length=%d' % len(data))

    def token(self):
        token = self.lexer_object.token()
        if token is not None:
            token.location = self.current_location.clone()
            self.current_location.update(token.value)

            self.log.debug('Got next token; value=%r, type=%s, location=%s' % (token.value, token.type, token.location))

        else:
            self.log.debug('End of file reached; location=%s' % self.current_location)

        return token

    def ignore_token(self, token):
        self.log.debug('Ignoring token; value=%r, type=%s, location=%s' % (token.value, token.type, self.current_location))
        self.current_location.update(token.value)

    @property
    def tokens(self):
        return self.token_list

    def t_error(self, t):
        token = t.value[0]
        self.error_context.error(replace(self.error_message, token=token), self.current_location.clone())

        self.current_location.update(token)
        self.lexer_object.skip(len(token))

        self.log.error('Error parsing character %r' % token)

    def get_location(self, position):
        data = self.lexer_object.lexdata

        # Note: I know at first it seems that the condition should be
        # position >= len(data) but actually len(data) is a valid
        # position since that points to the end of the input.
        if position > len(data):
            raise IndexError("Position invalid")

        nlpos = data.rfind('\n', 0, position)

        if nlpos == -1:
            return Location(self.source_name, 0, position, position)

        lineno = data.count('\n', 0, position)
        column = position - nlpos - 1
        return Location(self.source_name, lineno, column, position)

class LexerFactory(object):
    '''
    Create a Lexer object with the given settings.
    '''

    _tokens = None
    _literals = None
    _ignored = None

    _error_context = None
    _error_message = None

    def __init__(self):
        self._tokens = {}
        self._literals = set()
        self._ignored = set()

        self.log = logger.getLogger('lexer-factory-%d' % logger.sysid(self))
        self.log.info('Initialized lexer factory')

    def add_token(self, name, regexp):
        '''
        Add a list of tokens to parse.
        '''

        self._tokens[name] = regexp
        self.log.debug('Added token type %s; regex=%r' % (name, regexp))

    def add_ignore_token(self, name, *args, **kwargs):
        '''
        Add a list of tokens to be ignored.
        '''

        self._ignored.add(name)
        self.add_token(name, *args, **kwargs)
        self.log.debug('Added ignored token(s)')

    def add_literal(self, name, value, *args, **kwargs):
        '''
        Add literal tokens. Literal tokens are escaped before being added.
        '''

        self._literals.add(name)
        self.add_token(name, re.escape(value), *args, **kwargs)
        self.log.debug('Added literal(s)')

    def add_keyword(self, keyword):
        '''
        Add keywords. Keywords are tokens where the
        type is the uppercase of the keyword
        '''

        if not keyword_regex.match(keyword):
            raise ValueError("Keyword %r invalid", keyword)

        self.add_literal(keyword.upper(), keyword)
        self.log.debug("Added keyword token %s" % keyword)

    def set_error_context(self, context, message=None):
        '''
        Set error context with an error message template.
        '''

        self._error_context = context
        self._error_message = message
        self.log.debug("Set error context and message; context ID=%d, message=%r" % (logger.sysid(context), message))

    def __make_lex_member(self, expression, literal_state, action=None):
        '''
        Make a tokenizer function or string.
        '''

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
        '''
        Dynamically create a new lexer class.
        '''

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

            cls_dict['t_%s' % key] = self._tokens[key]

        if self._error_message is not None:
            cls_dict['error_message'] = self._error_message

        cls_dict['token_list'] = filter(lambda key: key not in self._ignored, self._tokens.keys())

        lexer_class = type('AutoLexer', (Lexer,), cls_dict)

        self.log.debug('Created lexer class; class ID=lexer-class-%d' % logger.sysid(lexer_class))
        return lexer_class

    def create(self, source_name):
        '''
        Create the new Lexer object.
        '''

        error_context = self._error_context or ErrorContext()
        cls = self.create_class()
        instance = cls(source_name, error_context)

        self.log.debug('Created lexer class; id=lexer-%d, context ID=%d' % (logger.sysid(instance), logger.sysid(error_context)))
        return instance
