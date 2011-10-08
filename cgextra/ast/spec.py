from ply.lex import lex, TOKEN, LexToken
from ply.yacc import yacc

from validators import collection, v_negate, v_and, v_or

class Location(object):
    def __init__(self, lineno, column, line):
        self.lineno = lineno
        self.column = column
        self.line = line

    @staticmethod
    def get_line_data(data, pos):
        pos = pos - data.count('\r\n')
        data = data.replace('\r\n', '\n')
        start = data.rfind('\n', 0, pos) + 1
        end = data.find('\n', start)
        if end == -1:
            end = len(data)

        return data[start:end], pos - start

    @classmethod
    def from_lexer(cls, lexer, token, lineno):
        line, col = Location.get_line_data(lexer.lexdata, lexer.lexpos)
        return cls(lineno, col, line)

    def highlight(self, token, highlight = '<>'):
        s, e = highlight
        self.line = self.line.replace(token, '%s%s%s' % (s, token, e))

    def __str__(self):
        return 'line %d column %d in %r' % (self.lineno + 1, self.column + 1, self.line)

class Error(object):
    def __init__(self, message, location):
        self._message = message
        self._location = location

    def __str__(self):
        return "%s (%s)" % (self._message, self._location)

class Lexer(object):
    keywords = {
        'and' : 'AND',
        'or' : 'OR',
        'not' : 'NOT',
        'node' : 'NODE',
        'required' : 'REQUIRED',
        'optional' : 'OPTIONAL',
        'from' : 'FROM',
        'pass' : 'PASS',
    }

    tokens = tuple(keywords.values()) + (
        'ID', 'STRING', 'INT',

        'LPAREN', 'RPAREN',
        'LBRACKET', 'RBRACKET',
        'COLON', 'DASH',

        'BLOCK_START', 'BLOCK_END',
    )

    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_COLON = r':'
    t_DASH = r'-'

    lineno = 0
    indent = 0
    errors = None
    eof = False
    level = 0

    @TOKEN(r'\#.*')
    def t_comment(self, token):
        pass

    @TOKEN(r'"([^"]|")*"')
    def t_STRING(self, token):
        token.value = token.value[1:-1].replace('\"', '"')
        return token

    @TOKEN(r'[a-zA-Z_][a-zA-Z0-9_]*')
    def t_ID(self, token):
        if token.value in self.keywords:
            token.type = self.keywords[token.value]

        return token

    @TOKEN(r'[0-9]+')
    def t_INT(self, token):
        token.value = int(token.value)
        return token

    @TOKEN(r'\s+')
    def t_whitespace(self, token):
        blocks = token.value.replace('\r\n', '\n').split('\n')
        self.lineno += len(blocks) - 1
        self.lexer.lineno = self.lineno

        if len(blocks) > 1:
            str = blocks[-1]
            indent = str.count(' ')
            indent += 4 * str.count('\t')

            if indent > self.indent:
                self.indent = indent
                token.type = 'BLOCK_START'
                self.level += 1
                return token

            if indent < self.indent:
                self.indent = indent
                token.type = 'BLOCK_END'
                self.level -= 1
                return token

    def __init__(self, **kwargs):
        try:
            del kwargs['module']

        except KeyError:
            pass

        self.lexer = lex(module = self)

    def input(self, data):
        self.errors = []
        self.lineno = 0
        self.eof = False
        self.level = 0
        self.lexer.input(data)

    def token(self):
        if self.eof:
            if self.level == 0:
                return None

            token = LexToken()
            token.type = 'BLOCK_END'
            token.value = ''
            token.lexpos = self.lexer.lexpos
            token.lineno = self.lineno
            self.level -= 1

            return token

        token = self.lexer.token()
        if token is None:
            self.eof = True
            return self.token()

        return token

    def t_error(self, token):
        location = Location.from_lexer(self.lexer, token, self.lineno)
        self.errors.append(Error("Invalid token %r" % token.value[0], location))
        self.lexer.skip(1)

class Parser(object):
    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'NOT'),
    )

    def __init__(self, lexer, **kwargs):
        try:
            del kwargs['module']

        except KeyError:
            pass

        self.errors = []

        self.lexer = lexer
        self.tokens = lexer.tokens

        self.yacc = yacc(module = self)

    def parse(self, module):
        self.module = module
        try:
            self.yacc.parse(lexer = self.lexer)
            return self.module

        finally:
            del self.module

    def p_start_0(self, p):
        '''start : '''

    def p_start_1(self, p):
        '''start : node start'''

    def __init_node(self, name, specs, base = None):
        required = set()
        optional = set()
        validate = {}
        for attribute, level, validator in specs:
            if level == 'optional':
                optional.add(attribute)

            else:
                required.add(attribute)

            validate[attribute] = validator

        self.module.make_type(name, required = required, optional = optional, validate = validate, base = base)

    def p_node_0(self, p):
        '''node : NODE ID COLON BLOCK_START node_spec BLOCK_END'''

        self.__init_node(p[2], p[5])

    def p_node_1(self, p):
        '''node : NODE ID FROM ID COLON BLOCK_START node_spec BLOCK_END'''

        self.__init_node(p[2], p[7], base = p[4])

    def p_node_spec_0(self, p):
        '''node_spec : '''

        p[0] = []

    def p_node_spec_1(self, p):
        '''node_spec : node_spec_entry node_spec'''

        p[0] = p[2]
        p[0].insert(0, p[1])

    def p_node_spec_2(self, p):
        '''node_spec : PASS'''

        p[0] = []

    def p_node_spec_entry(self, p):
        '''node_spec_entry : REQUIRED LPAREN validator_expr RPAREN ID
                           | OPTIONAL LPAREN validator_expr RPAREN ID'''

        p[0] = (p[5], p[1], p[3])

    def p_validator_expr_0(self, p):
        '''validator_expr : LPAREN validator_expr RPAREN'''

        p[0] = p[1]

    def p_validator_expr_1(self, p):
        '''validator_expr : validator_expr OR validator_expr'''

        p[0] = v_or(p[1], p[3])

    def p_validator_expr_2(self, p):
        '''validator_expr : validator_expr AND validator_expr'''

        p[0] = v_and(p[1], p[3])

    def p_validator_expr_3(self, p):
        '''validator_expr : NOT validator_expr'''

        p[0] = v_negate(p[2])

    def p_validator_expr_4(self, p):
        '''validator_expr : validator_expr LBRACKET range RBRACKET'''

        min, max = p[3]
        p[0] = collection(p[1], min = min, max = max)

    def p_validator_expr_5(self, p):
        '''validator_expr : validator_expr LBRACKET INT RBRACKET'''

        p[0] = collection(p[1], exact = p[3])

    def p_validator_expr_6(self, p):
        '''validator_expr : validator_expr LBRACKET RBRACKET'''

        p[0] = collection(p[1])

    def p_validator_expr_7(self, p):
        '''validator_expr : validator_expr LPAREN list RPAREN'''

        p[0] = p[1](*p[3])

    def p_validator_expr_concrete(self, p):
        '''validator_expr : ID'''

        if self.module.types.has_key(p[1]):
            type = self.module.types[p[1]]
            p[0] = lambda value: isinstance(value, type)

        elif self.module.validators.has_key(p[1]):
            p[0] = self.module.validators[p[1]]

        else:
            self.make_error(p[1], message = 'Missing type or validator %r' % p[1], pos = p.lexpos(1), lineno = p.lineno(1))

    def p_range_0(self, p):
        '''range : INT DASH INT'''

        p[0] = (p[1], p[3])

    def p_range_1(self, p):
        '''range : INT DASH'''

        p[0] = (p[1], None)

    def p_range_2(self, p):
        '''range : DASH INT'''

        return (None, p[2])

    def p_list_0(self, p):
        '''list : '''

        p[0] = []

    def p_list_1(self, p):
        '''list : INT list
                | STRING list
                | ID list'''

        p[0] = p[2]
        p[0].insert(0, p[1])

    def p_error(self, token):
        self.make_error(token)

    def make_error(self, token, message = None, pos = None, lineno = None):
        if not message:
            message = "Syntax error: %r" % token

        if pos is None:
            pos = self.lexer.lexer.lexpos

        if lineno is None:
            lineno = self.lexer.lineno

        line, col = Location.get_line_data(self.lexer.lexer.lexdata, pos)
        loc = Location(lineno, col, line)
        loc.highlight(token)
        self.errors.append(Error(message, loc))
