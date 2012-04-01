# THIS IS AN AUTOMATICALLY GENERATED FILE. ALL MANUAL MODIFICATIONS TO IT MAY
# BE LOST AT ANY TIME! MODIFY THE TEMPLATE INSTEAD (see below)
#
# Source file         calc.alp
# Parser class        codega.alp.generator:ScriptParser
# Target file         calcparser.py
# Generator class     codega.alp.generator:main_generator

__version__ = 'Unknown'
__language__ = 'Unknown'

__author__ = 'Unknown'
__email__ = 'Unknown'

from codega.alp.lexer import LexerFactory
from codega.alp.parser import ParserBase
from codega.alp.errorcontext import ErrorContext
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
lexer_factory.add_token('NAME', '[a-zA-Z_][a-zA-Z0-9]*');
lexer_factory.add_token('NUMBER', '(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?');
lexer_factory.add_literal('EQ', '=');
lexer_factory.add_literal('ADD', '+');
lexer_factory.add_literal('SUB', '-');
lexer_factory.add_literal('MUL', '*');
lexer_factory.add_literal('DIV', '/');
lexer_factory.add_literal('LPAREN', '(');
lexer_factory.add_literal('RPAREN', ')');
lexer_factory.add_keyword('for');
lexer_factory.add_keyword('do');
lexer_factory.add_keyword('to');
lexer_factory.add_keyword('step');
Lexer = lexer_factory.create_class()

# AST nodes
AstBaseClass = ast.create_base_node('AstBaseClass')
# Helper class for selectors!
def production(arg):
    return arg

# Helper class for selectors!
def expression(arg):
    return arg

class binary_expression(AstBaseClass):
    property_definitions = (
        ast.Property('operand0', klass=0),
        ast.Property('operator', klass=0),
        ast.Property('operand1', klass=0),
    )

class unary_expression(AstBaseClass):
    property_definitions = (
        ast.Property('operator', klass=0),
        ast.Property('operand', klass=0),
    )

class assignment(AstBaseClass):
    property_definitions = (
        ast.Property('rvalue', klass=0),
        ast.Property('lvalue', klass=0),
    )

class expr_for(AstBaseClass):
    property_definitions = (
        ast.Property('bound', klass=0),
        ast.Property('begin', klass=0),
        ast.Property('end', klass=0),
        ast.Property('step', klass=1),
        ast.Property('assignment', klass=0),
    )


# Parser
class Parser(ParserBase):
    start = 'production'

    precedence = (
        ('left', 'ADD', 'SUB'),
        ('left', 'DIV', 'MUL'),
        ('right', 'UMINUS'),
    )
    
    # Rules for node production
    rule_production_0 = rule.Rule('production', rule.RuleEntry('expression', key=None, ignore=None))
    def p_production_0(self, p):
        p[0] = self.rule_production_0(production, p[1:])
    p_production_0.__doc__ = rule_production_0.to_yacc_rule()

    rule_production_1 = rule.Rule('production', rule.RuleEntry('assignment', key=None, ignore=None))
    def p_production_1(self, p):
        p[0] = self.rule_production_1(production, p[1:])
    p_production_1.__doc__ = rule_production_1.to_yacc_rule()

    rule_production_2 = rule.Rule('production', rule.RuleEntry('expr_for', key=None, ignore=None))
    def p_production_2(self, p):
        p[0] = self.rule_production_2(production, p[1:])
    p_production_2.__doc__ = rule_production_2.to_yacc_rule()


    # Rules for node expression
    rule_expression_0 = rule.Rule('expression', rule.RuleEntry('binary_expression', key=None, ignore=None))
    def p_expression_0(self, p):
        p[0] = self.rule_expression_0(expression, p[1:])
    p_expression_0.__doc__ = rule_expression_0.to_yacc_rule()

    rule_expression_1 = rule.Rule('expression', rule.RuleEntry('unary_expression', key=None, ignore=None))
    def p_expression_1(self, p):
        p[0] = self.rule_expression_1(expression, p[1:])
    p_expression_1.__doc__ = rule_expression_1.to_yacc_rule()

    rule_expression_2 = rule.Rule('expression', rule.RuleEntry('NUMBER', key=None, ignore=None))
    def p_expression_2(self, p):
        p[0] = self.rule_expression_2(expression, p[1:])
    p_expression_2.__doc__ = rule_expression_2.to_yacc_rule()

    rule_expression_3 = rule.Rule('expression', rule.RuleEntry('NAME', key=None, ignore=None))
    def p_expression_3(self, p):
        p[0] = self.rule_expression_3(expression, p[1:])
    p_expression_3.__doc__ = rule_expression_3.to_yacc_rule()

    rule_expression_4 = rule.Rule('expression', rule.RuleEntry('LPAREN', key=None, ignore='-'), rule.RuleEntry('expression', key=None, ignore=None), rule.RuleEntry('RPAREN', key=None, ignore='-'))
    def p_expression_4(self, p):
        p[0] = self.rule_expression_4(expression, p[1:])
    p_expression_4.__doc__ = rule_expression_4.to_yacc_rule()


    # Rules for node binary_expression
    rule_binary_expression_0 = rule.Rule('binary_expression', rule.RuleEntry('expression', key=None, ignore=None), rule.RuleEntry('ADD', key=None, ignore=None), rule.RuleEntry('expression', key=None, ignore=None))
    def p_binary_expression_0(self, p):
        p[0] = self.rule_binary_expression_0(binary_expression, p[1:])
    p_binary_expression_0.__doc__ = rule_binary_expression_0.to_yacc_rule()

    rule_binary_expression_1 = rule.Rule('binary_expression', rule.RuleEntry('expression', key=None, ignore=None), rule.RuleEntry('SUB', key=None, ignore=None), rule.RuleEntry('expression', key=None, ignore=None))
    def p_binary_expression_1(self, p):
        p[0] = self.rule_binary_expression_1(binary_expression, p[1:])
    p_binary_expression_1.__doc__ = rule_binary_expression_1.to_yacc_rule()

    rule_binary_expression_2 = rule.Rule('binary_expression', rule.RuleEntry('expression', key=None, ignore=None), rule.RuleEntry('MUL', key=None, ignore=None), rule.RuleEntry('expression', key=None, ignore=None))
    def p_binary_expression_2(self, p):
        p[0] = self.rule_binary_expression_2(binary_expression, p[1:])
    p_binary_expression_2.__doc__ = rule_binary_expression_2.to_yacc_rule()

    rule_binary_expression_3 = rule.Rule('binary_expression', rule.RuleEntry('expression', key=None, ignore=None), rule.RuleEntry('DIV', key=None, ignore=None), rule.RuleEntry('expression', key=None, ignore=None))
    def p_binary_expression_3(self, p):
        p[0] = self.rule_binary_expression_3(binary_expression, p[1:])
    p_binary_expression_3.__doc__ = rule_binary_expression_3.to_yacc_rule()


    # Rules for node unary_expression
    rule_unary_expression_0 = rule.Rule('unary_expression', rule.RuleEntry('SUB', key=None, ignore=None), rule.RuleEntry('expression', key=None, ignore=None))
    rule_unary_expression_0.precedence = 'UMINUS'
    def p_unary_expression_0(self, p):
        p[0] = self.rule_unary_expression_0(unary_expression, p[1:])
    p_unary_expression_0.__doc__ = rule_unary_expression_0.to_yacc_rule()


    # Rules for node assignment
    rule_assignment_0 = rule.Rule('assignment', rule.RuleEntry('NAME', key=None, ignore=None), rule.RuleEntry('EQ', key=None, ignore='-'), rule.RuleEntry('expression', key=None, ignore=None))
    def p_assignment_0(self, p):
        p[0] = self.rule_assignment_0(assignment, p[1:])
    p_assignment_0.__doc__ = rule_assignment_0.to_yacc_rule()


    # Rules for node expr_for
    rule_expr_for_0 = rule.Rule('expr_for', rule.RuleEntry('FOR', key=None, ignore='-'), rule.RuleEntry('NAME', key='bound', ignore=None), rule.RuleEntry('EQ', key=None, ignore='-'), rule.RuleEntry('expression', key='begin', ignore=None), rule.RuleEntry('TO', key=None, ignore='-'), rule.RuleEntry('expression', key='end', ignore=None), rule.RuleEntry('DO', key=None, ignore='-'), rule.RuleEntry('assignment', key='assignment', ignore=None))
    def p_expr_for_0(self, p):
        p[0] = self.rule_expr_for_0(expr_for, p[1:])
    p_expr_for_0.__doc__ = rule_expr_for_0.to_yacc_rule()

    rule_expr_for_1 = rule.Rule('expr_for', rule.RuleEntry('FOR', key=None, ignore='-'), rule.RuleEntry('NAME', key='bound', ignore=None), rule.RuleEntry('EQ', key=None, ignore='-'), rule.RuleEntry('expression', key='begin', ignore=None), rule.RuleEntry('TO', key=None, ignore='-'), rule.RuleEntry('expression', key='end', ignore=None), rule.RuleEntry('STEP', key=None, ignore='-'), rule.RuleEntry('expression', key='step', ignore=None), rule.RuleEntry('DO', key=None, ignore='-'), rule.RuleEntry('assignment', key='assignment', ignore=None))
    def p_expr_for_1(self, p):
        p[0] = self.rule_expr_for_1(expr_for, p[1:])
    p_expr_for_1.__doc__ = rule_expr_for_1.to_yacc_rule()



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
