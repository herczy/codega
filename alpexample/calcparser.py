# THIS IS AN AUTOMATICALLY GENERATED FILE. ALL MANUAL MODIFICATIONS TO IT MAY
# BE LOST AT ANY TIME! MODIFY THE TEMPLATE INSTEAD (see below)
#
# Source file         calc.alp
# Parser class        codega.alp.generator.ScriptParser
# Target file         calcparser.py
# Generator class     codega.alp.generator.main_generator

__version__ = 'Unknown'
__language__ = 'Unknown'

__author__ = 'Unknown'
__email__ = 'Unknown'

from codega.alp.lexer import LexerFactory
from codega.alp.parser import ParserBase
from codega.alp.errorcontext import ErrorContext
from codega.alp import tools
from codega.alp import rule
from codega.alp import ast


class ParserError(Exception):
    '''Parse-related errors'''

    def __init__(self, ctx):
        super(ParserError, self).__init__('Parsing input failed')

        self.context = ctx

    def __str__(self):
        orig = super(ParserError, self).__str__()
        return '%s\n%s' % (orig, self.context.summary)

# Lexer
lexer_factory = LexerFactory()
lexer_factory.add_ignore_token('SPACES', '\s+');
lexer_factory.add_token('NAME', '[a-zA-Z_][a-zA-Z0-9]*')
lexer_factory.add_token('NUMBER', '(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?')
lexer_factory.add_literal('EQ', '=')
lexer_factory.add_literal('ADD', '+')
lexer_factory.add_literal('SUB', '-')
lexer_factory.add_literal('MUL', '*')
lexer_factory.add_literal('DIV', '/')
lexer_factory.add_literal('POW', '^')
lexer_factory.add_literal('COMMA', ',')
lexer_factory.add_literal('LPAREN', '(')
lexer_factory.add_literal('RPAREN', ')')
lexer_factory.add_keyword('for');
lexer_factory.add_keyword('do');
lexer_factory.add_keyword('to');
lexer_factory.add_keyword('step');
lexer_factory.add_keyword('def');
Lexer = lexer_factory.create_class()

# AST nodes
metainfo = ast.Metainfo()

# Helper class for selectors!
def production(arg):
    return arg

# Helper class for selectors!
def expression(arg):
    return arg

binary_expression_properties = (
    ('operand0', ast.REQUIRED),
    ('operator', ast.REQUIRED),
    ('operand1', ast.REQUIRED),
)
binary_expression_info = ast.Info('binary_expression', binary_expression_properties)
binary_expression = binary_expression_info.get_class(metainfo)

unary_expression_properties = (
    ('operator', ast.REQUIRED),
    ('operand', ast.REQUIRED),
)
unary_expression_info = ast.Info('unary_expression', unary_expression_properties)
unary_expression = unary_expression_info.get_class(metainfo)

call_properties = (
    ('func', ast.REQUIRED),
    ('args', ast.REQUIRED),
)
call_info = ast.Info('call', call_properties)
call = call_info.get_class(metainfo)

def exprlist(**kwargs):
    body = kwargs.pop('body', ())

    if 'head' in kwargs:
        head = kwargs.pop('head')
        body = (head,) + body

    if 'tail' in kwargs:
        tail = kwargs.pop('tail')
        body = body + (tail,)

    return body

def exprlist_tail(**kwargs):
    body = kwargs.pop('body', ())

    if 'head' in kwargs:
        head = kwargs.pop('head')
        body = (head,) + body

    if 'tail' in kwargs:
        tail = kwargs.pop('tail')
        body = body + (tail,)

    return body

assignment_properties = (
    ('rvalue', ast.REQUIRED),
    ('lvalue', ast.REQUIRED),
)
assignment_info = ast.Info('assignment', assignment_properties)
assignment = assignment_info.get_class(metainfo)

expr_for_properties = (
    ('bound', ast.REQUIRED),
    ('begin', ast.REQUIRED),
    ('end', ast.REQUIRED),
    ('step', ast.OPTIONAL),
    ('assignment', ast.REQUIRED),
)
expr_for_info = ast.Info('expr_for', expr_for_properties)
expr_for = expr_for_info.get_class(metainfo)

funcdef_properties = (
    ('name', ast.REQUIRED),
    ('args', ast.REQUIRED),
    ('expression', ast.REQUIRED),
)
funcdef_info = ast.Info('funcdef', funcdef_properties)
funcdef = funcdef_info.get_class(metainfo)

def id_list(**kwargs):
    body = kwargs.pop('body', ())

    if 'head' in kwargs:
        head = kwargs.pop('head')
        body = (head,) + body

    if 'tail' in kwargs:
        tail = kwargs.pop('tail')
        body = body + (tail,)

    return body

def id_list_tail(**kwargs):
    body = kwargs.pop('body', ())

    if 'head' in kwargs:
        head = kwargs.pop('head')
        body = (head,) + body

    if 'tail' in kwargs:
        tail = kwargs.pop('tail')
        body = body + (tail,)

    return body

number_properties = (
    ('value', ast.REQUIRED),
)
number_info = ast.Info('number', number_properties)
number = number_info.get_class(metainfo)


# Parser
class Parser(ParserBase):
    start = 'production'

    precedence = (
        ('left', 'ADD', 'SUB'),
        ('left', 'DIV', 'MUL'),
        ('right', 'POW'),
        ('right', 'UMINUS'),
    )
    
    # Rules for node production
    rule_production_0 = rule.Rule('production', rule.RuleEntry('expression', key=None, ignore=None))
    def p_production_0(self, p):
        p[0] = self.rule_production_0(production, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_production_0.__doc__ = rule_production_0.to_yacc_rule()

    rule_production_1 = rule.Rule('production', rule.RuleEntry('assignment', key=None, ignore=None))
    def p_production_1(self, p):
        p[0] = self.rule_production_1(production, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_production_1.__doc__ = rule_production_1.to_yacc_rule()

    rule_production_2 = rule.Rule('production', rule.RuleEntry('expr_for', key=None, ignore=None))
    def p_production_2(self, p):
        p[0] = self.rule_production_2(production, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_production_2.__doc__ = rule_production_2.to_yacc_rule()

    rule_production_3 = rule.Rule('production', rule.RuleEntry('funcdef', key=None, ignore=None))
    def p_production_3(self, p):
        p[0] = self.rule_production_3(production, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_production_3.__doc__ = rule_production_3.to_yacc_rule()


    # Rules for node expression
    rule_expression_0 = rule.Rule('expression', rule.RuleEntry('binary_expression', key=None, ignore=None))
    def p_expression_0(self, p):
        p[0] = self.rule_expression_0(expression, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_expression_0.__doc__ = rule_expression_0.to_yacc_rule()

    rule_expression_1 = rule.Rule('expression', rule.RuleEntry('unary_expression', key=None, ignore=None))
    def p_expression_1(self, p):
        p[0] = self.rule_expression_1(expression, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_expression_1.__doc__ = rule_expression_1.to_yacc_rule()

    rule_expression_2 = rule.Rule('expression', rule.RuleEntry('call', key=None, ignore=None))
    def p_expression_2(self, p):
        p[0] = self.rule_expression_2(expression, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_expression_2.__doc__ = rule_expression_2.to_yacc_rule()

    rule_expression_3 = rule.Rule('expression', rule.RuleEntry('number', key=None, ignore=None))
    def p_expression_3(self, p):
        p[0] = self.rule_expression_3(expression, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_expression_3.__doc__ = rule_expression_3.to_yacc_rule()

    rule_expression_4 = rule.Rule('expression', rule.RuleEntry('NAME', key=None, ignore=None))
    def p_expression_4(self, p):
        p[0] = self.rule_expression_4(expression, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_expression_4.__doc__ = rule_expression_4.to_yacc_rule()

    rule_expression_5 = rule.Rule('expression', rule.RuleEntry('LPAREN', key=None, ignore='-'), rule.RuleEntry('expression', key=None, ignore=None), rule.RuleEntry('RPAREN', key=None, ignore='-'))
    def p_expression_5(self, p):
        p[0] = self.rule_expression_5(expression, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_expression_5.__doc__ = rule_expression_5.to_yacc_rule()


    # Rules for node binary_expression
    rule_binary_expression_0 = rule.Rule('binary_expression', rule.RuleEntry('expression', key=None, ignore=None), rule.RuleEntry('ADD', key=None, ignore=None), rule.RuleEntry('expression', key=None, ignore=None))
    def p_binary_expression_0(self, p):
        p[0] = self.rule_binary_expression_0(binary_expression, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_binary_expression_0.__doc__ = rule_binary_expression_0.to_yacc_rule()

    rule_binary_expression_1 = rule.Rule('binary_expression', rule.RuleEntry('expression', key=None, ignore=None), rule.RuleEntry('SUB', key=None, ignore=None), rule.RuleEntry('expression', key=None, ignore=None))
    def p_binary_expression_1(self, p):
        p[0] = self.rule_binary_expression_1(binary_expression, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_binary_expression_1.__doc__ = rule_binary_expression_1.to_yacc_rule()

    rule_binary_expression_2 = rule.Rule('binary_expression', rule.RuleEntry('expression', key=None, ignore=None), rule.RuleEntry('MUL', key=None, ignore=None), rule.RuleEntry('expression', key=None, ignore=None))
    def p_binary_expression_2(self, p):
        p[0] = self.rule_binary_expression_2(binary_expression, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_binary_expression_2.__doc__ = rule_binary_expression_2.to_yacc_rule()

    rule_binary_expression_3 = rule.Rule('binary_expression', rule.RuleEntry('expression', key=None, ignore=None), rule.RuleEntry('DIV', key=None, ignore=None), rule.RuleEntry('expression', key=None, ignore=None))
    def p_binary_expression_3(self, p):
        p[0] = self.rule_binary_expression_3(binary_expression, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_binary_expression_3.__doc__ = rule_binary_expression_3.to_yacc_rule()

    rule_binary_expression_4 = rule.Rule('binary_expression', rule.RuleEntry('expression', key=None, ignore=None), rule.RuleEntry('POW', key=None, ignore=None), rule.RuleEntry('expression', key=None, ignore=None))
    def p_binary_expression_4(self, p):
        p[0] = self.rule_binary_expression_4(binary_expression, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_binary_expression_4.__doc__ = rule_binary_expression_4.to_yacc_rule()


    # Rules for node unary_expression
    rule_unary_expression_0 = rule.Rule('unary_expression', rule.RuleEntry('SUB', key=None, ignore=None), rule.RuleEntry('expression', key=None, ignore=None))
    rule_unary_expression_0.precedence = 'UMINUS'
    def p_unary_expression_0(self, p):
        p[0] = self.rule_unary_expression_0(unary_expression, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_unary_expression_0.__doc__ = rule_unary_expression_0.to_yacc_rule()


    # Rules for node call
    rule_call_0 = rule.Rule('call', rule.RuleEntry('NAME', key=None, ignore=None), rule.RuleEntry('LPAREN', key=None, ignore='-'), rule.RuleEntry('exprlist', key=None, ignore=None), rule.RuleEntry('RPAREN', key=None, ignore='-'))
    def p_call_0(self, p):
        p[0] = self.rule_call_0(call, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_call_0.__doc__ = rule_call_0.to_yacc_rule()


    # Rules for node exprlist
    rule_exprlist_0 = rule.Rule('exprlist')
    def p_exprlist_0(self, p):
        p[0] = self.rule_exprlist_0(exprlist, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_exprlist_0.__doc__ = rule_exprlist_0.to_yacc_rule()

    rule_exprlist_1 = rule.Rule('exprlist', rule.RuleEntry('exprlist_tail', key='body', ignore=None))
    def p_exprlist_1(self, p):
        p[0] = self.rule_exprlist_1(exprlist, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_exprlist_1.__doc__ = rule_exprlist_1.to_yacc_rule()


    # Rules for node exprlist_tail
    rule_exprlist_tail_0 = rule.Rule('exprlist_tail', rule.RuleEntry('expression', key='head', ignore=None))
    def p_exprlist_tail_0(self, p):
        p[0] = self.rule_exprlist_tail_0(exprlist_tail, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_exprlist_tail_0.__doc__ = rule_exprlist_tail_0.to_yacc_rule()

    rule_exprlist_tail_1 = rule.Rule('exprlist_tail', rule.RuleEntry('expression', key='head', ignore=None), rule.RuleEntry('COMMA', key=None, ignore='-'), rule.RuleEntry('exprlist_tail', key='body', ignore=None))
    def p_exprlist_tail_1(self, p):
        p[0] = self.rule_exprlist_tail_1(exprlist_tail, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_exprlist_tail_1.__doc__ = rule_exprlist_tail_1.to_yacc_rule()


    # Rules for node assignment
    rule_assignment_0 = rule.Rule('assignment', rule.RuleEntry('NAME', key=None, ignore=None), rule.RuleEntry('EQ', key=None, ignore='-'), rule.RuleEntry('expression', key=None, ignore=None))
    def p_assignment_0(self, p):
        p[0] = self.rule_assignment_0(assignment, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_assignment_0.__doc__ = rule_assignment_0.to_yacc_rule()


    # Rules for node expr_for
    rule_expr_for_0 = rule.Rule('expr_for', rule.RuleEntry('FOR', key=None, ignore='-'), rule.RuleEntry('NAME', key='bound', ignore=None), rule.RuleEntry('EQ', key=None, ignore='-'), rule.RuleEntry('expression', key='begin', ignore=None), rule.RuleEntry('TO', key=None, ignore='-'), rule.RuleEntry('expression', key='end', ignore=None), rule.RuleEntry('DO', key=None, ignore='-'), rule.RuleEntry('assignment', key='assignment', ignore=None))
    def p_expr_for_0(self, p):
        p[0] = self.rule_expr_for_0(expr_for, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_expr_for_0.__doc__ = rule_expr_for_0.to_yacc_rule()

    rule_expr_for_1 = rule.Rule('expr_for', rule.RuleEntry('FOR', key=None, ignore='-'), rule.RuleEntry('NAME', key='bound', ignore=None), rule.RuleEntry('EQ', key=None, ignore='-'), rule.RuleEntry('expression', key='begin', ignore=None), rule.RuleEntry('TO', key=None, ignore='-'), rule.RuleEntry('expression', key='end', ignore=None), rule.RuleEntry('STEP', key=None, ignore='-'), rule.RuleEntry('expression', key='step', ignore=None), rule.RuleEntry('DO', key=None, ignore='-'), rule.RuleEntry('assignment', key='assignment', ignore=None))
    def p_expr_for_1(self, p):
        p[0] = self.rule_expr_for_1(expr_for, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_expr_for_1.__doc__ = rule_expr_for_1.to_yacc_rule()


    # Rules for node funcdef
    rule_funcdef_0 = rule.Rule('funcdef', rule.RuleEntry('DEF', key=None, ignore='-'), rule.RuleEntry('NAME', key=None, ignore=None), rule.RuleEntry('LPAREN', key=None, ignore='-'), rule.RuleEntry('id_list', key=None, ignore=None), rule.RuleEntry('RPAREN', key=None, ignore='-'), rule.RuleEntry('EQ', key=None, ignore='-'), rule.RuleEntry('expression', key=None, ignore=None))
    def p_funcdef_0(self, p):
        p[0] = self.rule_funcdef_0(funcdef, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_funcdef_0.__doc__ = rule_funcdef_0.to_yacc_rule()


    # Rules for node id_list
    rule_id_list_0 = rule.Rule('id_list')
    def p_id_list_0(self, p):
        p[0] = self.rule_id_list_0(id_list, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_id_list_0.__doc__ = rule_id_list_0.to_yacc_rule()

    rule_id_list_1 = rule.Rule('id_list', rule.RuleEntry('id_list_tail', key='body', ignore=None))
    def p_id_list_1(self, p):
        p[0] = self.rule_id_list_1(id_list, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_id_list_1.__doc__ = rule_id_list_1.to_yacc_rule()


    # Rules for node id_list_tail
    rule_id_list_tail_0 = rule.Rule('id_list_tail', rule.RuleEntry('NAME', key='head', ignore=None))
    def p_id_list_tail_0(self, p):
        p[0] = self.rule_id_list_tail_0(id_list_tail, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_id_list_tail_0.__doc__ = rule_id_list_tail_0.to_yacc_rule()

    rule_id_list_tail_1 = rule.Rule('id_list_tail', rule.RuleEntry('NAME', key='head', ignore=None), rule.RuleEntry('COMMA', key=None, ignore='-'), rule.RuleEntry('id_list_tail', key='body', ignore=None))
    def p_id_list_tail_1(self, p):
        p[0] = self.rule_id_list_tail_1(id_list_tail, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_id_list_tail_1.__doc__ = rule_id_list_tail_1.to_yacc_rule()


    # Rules for node number
    rule_number_0 = rule.Rule('number', rule.RuleEntry('NUMBER', key=None, ignore=None))
    def p_number_0(self, p):
        p[0] = self.rule_number_0(number, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_number_0.__doc__ = rule_number_0.to_yacc_rule()



def parse(sourcename, data):
    errctx = ErrorContext()
    lexer = Lexer(sourcename, errctx)
    parser = Parser(lexer)

    parser.input(data)
    res = parser.parse()

    if not errctx.result:
        raise ParserError(errctx)

    return res

def parse_file(filename):
    return parse(sourcename=filename, data=open(filename).read())
