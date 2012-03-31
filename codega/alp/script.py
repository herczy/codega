import types

from lexer import Lexer

from parser import ParserBase
from codega.ordereddict import OrderedDict
from codega.alp import ast, rule
from codega.alp.lexer import LexerFactory
from codega.decorators import set_attributes, define, bind
from codega.alp.errorcontext import ErrorContext

class ParserError(Exception):
    '''Parse-related errors'''

    def __init__(self, ctx):
        super(ParserError, self).__init__('Parsing input failed')

        self.context = ctx

    def __str__(self):
        orig = super(ParserError, self).__str__()
        return '%s\n%s' % (orig, self.context.summary)

class ScriptLexer(Lexer):
    t_ignore = ' \r\n\t'

    keywords = (
        # Python-style import statements
        'from', 'import', 'as',

        # Tokenizer part
        'token', 'keyword', 'literal', 'ignore',

        # Node types
        'node', 'selection',

        # Properties
        'optional', 'required',

        # Rule definition
        'rule', 'start',

        # Precedence
        'precedence',
        ('PRECDIR', 'left', 'right'),

        # Script information keywords
        ('INFOKEYWORD', 'language', 'author', 'version', 'email', 'name'),
    )

    kwmap = {}

    for keyword in keywords:
        if isinstance(keyword, basestring):
            kwmap[keyword] = keyword.upper()

        else:
            _token, keyword_collection = keyword[0], keyword[1:]

            for keyword in keyword_collection:
                kwmap[keyword] = _token

    tokens = (
        'ID', 'STRING', 'INTEGER',
        'SEMICOLON', 'ARROW', 'MINUS', 'EQ', 'PERIOD', 'COMMA',
        'PRECSYM',
        'LCURLY', 'RCURLY',
        'LPAREN', 'RPAREN',
    ) + tuple(kwmap.values())

    t_SEMICOLON = r';'
    t_ARROW = r'=>'
    t_MINUS = r'-'
    t_EQ = r'='
    t_PERIOD = r'\.'
    t_COMMA = r','
    t_LCURLY = r'{'
    t_RCURLY = r'}'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'

    t_PRECSYM = r'%prec'

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'

        if t.value in self.kwmap:
            t.type = self.kwmap[t.value]

        return t

    def t_STRING(self, t):
        r'\'([^\'\\]+|\\.)*\''

        t.value = t.value[1:-1].decode('string_escape')
        return t

    def t_INTEGER(self, t):
        r'[+-]?(0|[1-9][0-9]*)'

        t.value = int(t.value)
        return t

    def t_COMMENT(self, t):
        r'\#.*?\n'

class ScriptParser(ParserBase):
    start = 'start'

    def __init__(self, *args, **kwargs):
        super(ScriptParser, self).__init__(*args, **kwargs)

        self._info = OrderedDict()
        self._modules = OrderedDict()
        self._lexerfactory = LexerFactory()
        self._baseclass = ast.create_base_node('ScriptBase')
        self._selections = []

        self._precedence = []
        self._start = 'start'

    def create_module(self, name):
        mod = types.ModuleType(name)

        for name, cls in self._baseclass.metainfo.classes:
            setattr(mod, name, cls)

        mod.__info__ = self._info
        mod.__modules__ = self._modules
        mod.__metainfo__ = self._baseclass.metainfo

        mod.__lexer__ = self._lexerfactory.create_class()
        mod.__parser__ = self.create_parser()

        @define(mod)
        @bind(mod, pos=0)
        def parse(mod, sourcename, data):
            errctx = ErrorContext()
            lexer = mod.__lexer__(sourcename, errctx)
            parser = mod.__parser__(lexer)

            parser.input(data)
            res = parser.parse()

            if not errctx.result:
                raise ParserError(errctx)

            return res

        @define(mod)
        @bind(mod, pos=0)
        def parse_file(mod, filename):
            return mod.parse(sourcename=filename, data=open(filename).read())

        return mod

    def create_class_handler_function(self, name, cls, rule, index):
        @set_attributes('p_%s_%d' % (name, index), rule.to_yacc_rule())
        def rule_handler(self, prod):
            prod[0] = rule(cls, prod[1:])

        return rule_handler

    def create_selection_handler_function(self, name, rule, index):
        @set_attributes('p_%s_%d' % (name, index), rule.to_yacc_rule())
        def rule_handler(self, prod):
            args, kwargs = rule.create_argument_list(prod[1:])
            if kwargs:
                raise ValueError("Selection cannot have keyword argument")

            if len(args) != 1:
                raise ValueError("Invalid number of values")

            prod[0] = args[0]

        return rule_handler

    def create_parser(self, name='Parser'):
        meta = self._baseclass.metainfo

        bind_members = {}
        prec = dict()
        for name, cls in meta.classes:
            for index, rule in enumerate(cls.rules):
                func = self.create_class_handler_function(name, cls, rule, index)
                define(bind_members)(func)

        for name, ruleset in self._selections:
            for index, rule in enumerate(ruleset):
                func = self.create_selection_handler_function(name, rule, index)
                bind_members[func.__name__] = func

        if self._precedence:
            prec = []

            for dir, values in self._precedence:
                prec.append((dir,) + tuple(values))

            bind_members['precedence'] = tuple(prec)

        bind_members['start'] = self._start
        return ParserBase.subclass(name, bind_members)

    def p_start(self, p):
        '''start : header body'''

    def p_header_0(self, p):
        '''header : '''

    def p_header_1(self, p):
        '''header : header_entry SEMICOLON header'''

    def p_header_entry(self, p):
        '''header_entry : INFOKEYWORD ID'''

        self._info.insert(0, p[1], p[2])

    def p_body_0(self, p):
        '''body : '''

    def p_body_1(self, p):
        '''body : main_entry SEMICOLON body'''

    def p_main_entry_import_0(self, p):
        '''main_entry : IMPORT module'''

        self._modules[p[2]] = __import__(p[2])

    def p_main_entry_import_1(self, p):
        '''main_entry : FROM module IMPORT ID'''

        self._modules[p[4]] = __import__(p[4], fromlist=[p[2]])

    def p_main_entry_import_2(self, p):
        '''main_entry : FROM module IMPORT ID AS ID'''

        self._modules[p[6]] = __import__(p[4], fromlist=[p[2]])

    def p_main_entry_start(self, p):
        '''main_entry : START ID'''

        self._start = p[2]

    def p_main_entry_token(self, p):
        '''main_entry : TOKEN ID STRING'''

        self._lexerfactory.add_token(p[2], p[3])

    def p_main_entry_literal(self, p):
        '''main_entry : LITERAL ID STRING'''

        self._lexerfactory.add_literal(p[2], p[3])

    def p_main_entry_keyword(self, p):
        '''main_entry : KEYWORD ID'''

        self._lexerfactory.add_keyword(p[2])

    def p_main_entry_ignore(self, p):
        '''main_entry : IGNORE ID STRING'''

        self._lexerfactory.add_ignore_token(p[2], p[3])

    def p_main_entry_precedence(self, p):
        '''main_entry : PRECEDENCE PRECDIR LPAREN idlist RPAREN'''

        self._precedence.append((p[2], p[4]))

    def make_rules(self, name, *ruleset):
        res = []

        for entries, prec in ruleset:
            r = rule.Rule(name, *entries)
            if prec is not None:
                r.precedence = prec

            res.append(r)

        return res

    def p_main_entry_node(self, p):
        '''main_entry : NODE ID LCURLY node_body RCURLY'''

        props, rule_entries = p[4]
        self._baseclass.subclass(p[2], rules=self.make_rules(p[2], *rule_entries), property_definitions=props)

    def p_main_entry_selection(self, p):
        '''main_entry : SELECTION ID LCURLY rule_list RCURLY'''

        self._selections.append((p[2], self.make_rules(p[2], *p[4])))

    def p_main_node_body(self, p):
        '''node_body : property_list rule_list'''

        p[0] = (p[1], p[2])

    def p_property_list_0(self, p):
        '''property_list : '''

        p[0] = ()

    def p_property_list_1(self, p):
        '''property_list : OPTIONAL ID SEMICOLON property_list
                         | REQUIRED ID SEMICOLON property_list'''

        prop = ast.Property(p[2], klass=ast.Property.get_class_value(p[1]))
        p[0] = (prop,) + p[4]

    def p_rule_list_0(self, p):
        '''rule_list : '''

        p[0] = ()

    def p_rule_list_1(self, p):
        '''rule_list : RULE rule_entries SEMICOLON rule_list'''

        p[0] = ((p[2], None),) + p[4]

    def p_rule_list_2(self, p):
        '''rule_list : RULE rule_entries PRECSYM ID SEMICOLON rule_list'''

        p[0] = ((p[2], p[4]),) + p[6]

    def p_rule_entries_0(self, p):
        '''rule_entries : '''

        p[0] = ()

    def p_rule_entries_1(self, p):
        '''rule_entries : rule_entry rule_entries'''

        p[0] = (p[1],) + p[2]

    def p_rule_entry_nokey(self, p):
        '''rule_entry : ID'''

        p[0] = rule.RuleEntry(p[1])

    def p_rule_entry_ignored(self, p):
        '''rule_entry : MINUS ID'''

        p[0] = rule.RuleEntry(p[2], ignore=True)

    def p_rule_entry_withkey(self, p):
        '''rule_entry : ID EQ ID'''

        p[0] = rule.RuleEntry(p[3], key=p[1])

    def p_module_0(self, p):
        '''module : ID'''

        p[0] = p[1]

    def p_module_1(self, p):
        '''module : ID PERIOD module'''

        p[0] = ''.join(p[1:])

    def p_idlist_0(self, p):
        '''idlist : ID'''

        p[0] = (p[1],)

    def p_idlist_1(self, p):
        '''idlist : ID COMMA idlist'''

        p[0] = (p[1],) + p[3]

def parse(sourcename, data, name=None):
    errctx = ErrorContext()
    lexer = ScriptLexer(sourcename, errctx)
    parser = ScriptParser(lexer)

    parser.input(data)
    parser.parse()

    if not errctx.result:
        raise ParserError(errctx)

    if name is None:
        name = sourcename

    return parser.create_module(name)

def parse_file(filename, name=None):
    return parse(filename, open(filename).read(), name=name)
