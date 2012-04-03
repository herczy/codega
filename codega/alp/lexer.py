import re

from ply import lex
from ply.lex import TOKEN

from codega.immutable import Immutable
from codega.ordereddict import OrderedDict
from codega.decorators import abstract

from location import Location
from errorcontext import ErrorContext
from tools import replace
import logger

keyword_regex = re.compile('^[a-zA-Z_][a-zA-Z0-9_]*$')

class NoMatchError(Exception):
    '''No match was found'''

class Token(Immutable):
    def __init__(self, lexer, type, value, location):
        self.lexer = lexer
        self.type = type
        self.value = value
        self.location = location.clone()

        super(Token, self).__init__()

    @property
    def lineno(self):
        return self._location.lineno

    @property
    def lexpos(self):
        return self._location.lineno

    def __str__(self):
        return self.value

    def __repr__(self):
        return '%s(%r, type=%s, location=%s)' % (self.__class__.__name__, self.value, self.type, self.location)

class MatchBase(Immutable):
    def __init__(self, type):
        self.type = type

        super(MatchBase, self).__init__()

    def tokens(self):
        return set((self.type,))

    @abstract
    def match(self, data):
        pass

    def __str__(self):
        return 'match.%s' % self.type

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self)

class LiteralMatch(MatchBase):
    def __init__(self, type, values):
        for value in values:
            if not isinstance(value, basestring) or value == '':
                raise ValueError('Literal matcher only accepts non-empty strings')

        self.values = values

        super(LiteralMatch, self).__init__(type)

    def match(self, data):
        for val in self.values:
            if data.startswith(val):
                return self, val

        raise NoMatchError('Literal not matched')

    def __str__(self):
        return 'literal.%s(%s)' % (self.type, ', '.join(repr(s) for s in self.values))

class RegexMatch(MatchBase):
    def __init__(self, type, regex):
        self.regex = regex
        self.matcher = re.compile(regex)

        if self.matcher.match(''):
            raise ValueError('Regex matcher cannot match empty strings')

        super(RegexMatch, self).__init__(type)

    def match(self, data):
        match = self.matcher.match(data)
        if not match:
            raise NoMatchError('No match found')

        begin, end = match.span()
        assert begin == 0

        return self, data[begin:end]

    def __str__(self):
        return 'regex.%s(%r)' % (self.type, self.regex)

class ProxyMatch(MatchBase):
    def __init__(self, matcher):
        self.matcher = matcher

        super(ProxyMatch, self).__init__(self.matcher.type)

    def tokens(self):
        return self.matcher.tokens()

    def match(self, data):
        _, value = self.matcher.match(data)
        return self, value

    def __str__(self):
        return 'proxy(%s)' % (self.matcher)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.matcher)

class IgnoreMatch(ProxyMatch):
    def __str__(self):
        return 'ignore(%s)' % (self.matcher)

class GroupMatch(MatchBase):
    def __init__(self, entries, master=None):
        self.master = master
        self.entries = entries

        super(GroupMatch, self).__init__(None)

    def tokens(self):
        res = set()
        if self.master is not None:
            res.update(self.master.tokens())

        for matcher in self.entries:
            res.update(matcher.tokens())

        return res

    def submatch(self, data):
        for matcher in self.entries:
            try:
                return matcher.match(data)

            except NoMatchError:
                pass

        raise NoMatchError('No match found in subgroups')

    def match(self, data):
        if self.master is None:
            return self.submatch(data)

        matcher, value = self.master.match(data)

        try:
            submatcher, subvalue = self.submatch(value)

            if subvalue == value:
                return submatcher, subvalue

        except NoMatchError:
            pass

        return matcher, value

    def __str__(self):
        if self.master is None:
            return 'group(%s)' % (', '.join(str(s) for s in self.entries))

        else:
            return 'group(master=%s, %s)' % (self.master, ', '.join(str(s) for s in self.entries))

    def __repr__(self):
        if self.master is None:
            return '%s(%s)' % (self.__class__.__name__, ', '.join(repr(s) for s in self.entries))

        else:
            return '%s(master=%r, %s)' % (self.__class__.__name__, ', '.join(repr(s) for s in self.entries))

class Lexer(object):
    _matcher = None
    _conversions = None
    _buffer = None
    _location = None

    error_message = 'Invalid token: @token@'

    def __init__(self, source_name, error_context):
        self.source_name = source_name
        self.error_context = error_context

        self.log = logger.getLogger('lexer-%d' % logger.sysid(self))
        self.log.info('Created lexer; class ID=lexer-class-%d' % logger.sysid(self.__class__))

    @property
    def buffer(self):
        return self._buffer

    @property
    def tokens(self):
        return tuple(self._matcher.tokens())

    def input(self, data):
        self._buffer = data
        self._location = Location(self.source_name, 0, 0, 0)

        self.log.debug('Got new input; length=%d' % len(data))

    def reset(self):
        self._buffer = None
        self._location = None

        self.log.debug('Object has been reseted')

    def skip(self, length):
        self._location.update(self._buffer[:length])
        self._buffer = self._buffer[length:]

    def token(self):
        assert self._buffer is not None
        assert self._location is not None

        while True:
            if self._buffer == '':
                self.log.debug('End of file reached; location=%s' % self._location)
                return None

            buffer_size = len(self._buffer)
            try:
                matcher, value = self._matcher.match(self._buffer)

            except NoMatchError:
                self.on_lexer_error()

                if buffer_size == len(self._buffer):
                    raise

                continue

            location = self._location.clone()
            self.skip(len(value))
            if not isinstance(matcher, IgnoreMatch):
                break

            else:
                self.log.debug('Ignoring token; matcher=%r, value=%r, location=%s' % (matcher, value, location))

        for conv in self._conversions:
            value = conv(value)

        token = Token(self, matcher.type, value, location)
        self.log.debug('Got next token: %r' % token)
        return token

    def on_lexer_error(self):
        token = self.buffer[0]
        self.error_context.error(replace(self.error_message, token=token), self.current_location.clone())
        self.log.error('Error parsing character %r' % token)

        self.skip(1)

class LexerFactory(object):
    '''
    Create a Lexer object with the given settings.
    '''

    _tokens = None
    _literals = None
    _ignored = None
    _conversions = None

    _error_context = None
    _error_message = None

    def __init__(self):
        self._tokens = OrderedDict()
        self._literals = OrderedDict()
        self._ignored = OrderedDict()
        self._conversions = OrderedDict()

        self.log = logger.getLogger('lexer-factory-%d' % logger.sysid(self))
        self.log.info('Initialized lexer factory')

    def add_token(self, name, regexp):
        '''
        Add a list of tokens to parse.
        '''

        self._tokens[name] = regexp
        self.log.debug('Added token type %s; regex=%r' % (name, regexp))

    def add_ignore_token(self, name, regexp):
        '''
        Add a list of tokens to be ignored.
        '''

        self._ignored[name] = regexp
        self.log.debug('Added ignored token type %s; regex=%r' % (name, regexp))

    def add_literal(self, name, value):
        '''
        Add literal tokens. Literal tokens are escaped before being added.
        '''

        self._literals[name] = value
        self.log.debug('Added literal type %s; literal=%r' % (name, value))

    def add_keyword(self, keyword):
        '''
        Add keywords. Keywords are tokens where the
        type is the uppercase of the keyword
        '''

        if not keyword_regex.match(keyword):
            raise ValueError("Keyword %r invalid", keyword)

        self.add_literal(keyword.upper(), keyword)
        self.log.debug("Added keyword token %s" % keyword)

    def add_conversion(self, name, conversion):
        '''
        Add a conversion function to the lexer.
        '''

        self._conversions.setdefault(name, [])
        self._conversions[name].append(conversion)

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

        matchers = []
        literals = list(self._literals.keys())

        for key, value in self._tokens.items():
            self.log.debug("Binding token %s(%r); remaining literals: %s" % (key, value, ', '.join(literals)))

            matcher = RegexMatch(key, value)
            matched_literals = []
            for key in literals:
                try:
                    matcher.match(self._literals[key])

                except NoMatchError:
                    continue

                matched_literals.append(key)

            if matched_literals:
                literal_matchers = []
                for key in matched_literals:
                    literal_matchers.append(LiteralMatch(key, (self._literals[key],)))
                    literals.remove(key)

                matcher = GroupMatch(literal_matchers, master=matcher)

            matchers.append(matcher)

        for key in literals:
            self.log.debug("Binding remaining literal token %s" % key)
            matchers.append(LiteralMatch(key, (self._literals[key],)))

        matchers.append(IgnoreMatch(RegexMatch('ignored', '(%s)' % '|'.join('(%s)' % v for v in self._ignored.values()))))

        cls_dict = {}
        cls_dict['_matcher'] = GroupMatch(matchers)
        cls_dict['_conversions'] = self._conversions

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
