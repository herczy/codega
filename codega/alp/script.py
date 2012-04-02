# THIS IS AN AUTOMATICALLY GENERATED FILE. ALL MANUAL MODIFICATIONS TO IT MAY
# BE LOST AT ANY TIME! MODIFY THE TEMPLATE INSTEAD (see below)
#
# Source file         alplang.alp
# Parser class        codega.alp.generator:ScriptParser
# Target file         script.py
# Generator class     codega.alp.generator:main_generator

__version__ = '2'
__language__ = 'alp'

__author__ = 'Hercinger Viktor'
__email__ = 'hercinger.viktor@gmail.com'

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
lexer_factory.add_ignore_token('SPACES', '\\s+');
lexer_factory.add_ignore_token('COMMENTS', '\\#.*?\\n');
lexer_factory.add_literal('FROM', 'from');
lexer_factory.add_literal('IMPORT', 'import');
lexer_factory.add_literal('AS', 'as');
lexer_factory.add_literal('TOKEN', 'token');
lexer_factory.add_literal('KEYWORD', 'keyword');
lexer_factory.add_literal('LITERAL', 'literal');
lexer_factory.add_literal('IGNORE', 'ignore');
lexer_factory.add_literal('NODE', 'node');
lexer_factory.add_literal('LIST', 'list');
lexer_factory.add_literal('SELECTION', 'selection');
lexer_factory.add_literal('OPTIONAL', 'optional');
lexer_factory.add_literal('REQUIRED', 'required');
lexer_factory.add_literal('RULE', 'rule');
lexer_factory.add_literal('START', 'start');
lexer_factory.add_literal('PRECEDENCE', 'precedence');
lexer_factory.add_literal('LEFT', 'left');
lexer_factory.add_literal('RIGHT', 'right');
lexer_factory.add_literal('LANGUAGE', 'language');
lexer_factory.add_literal('AUTHOR', 'author');
lexer_factory.add_literal('VERSION', 'version');
lexer_factory.add_literal('EMAIL', 'email');
lexer_factory.add_literal('SEMICOLON', ';');
lexer_factory.add_literal('COLON', ',');
lexer_factory.add_literal('ARROW', '=>');
lexer_factory.add_literal('MINUS', '-');
lexer_factory.add_literal('EQ', '=');
lexer_factory.add_literal('PERIOD', '.');
lexer_factory.add_literal('COMMA', ':');
lexer_factory.add_literal('LCURLY', '{');
lexer_factory.add_literal('RCURLY', '}');
lexer_factory.add_literal('LPAREN', '(');
lexer_factory.add_literal('RPAREN', ')');
lexer_factory.add_literal('PRECSYM', '%prec');
lexer_factory.add_token('ID', '[a-zA-Z_][a-zA-Z0-9_]*');
lexer_factory.add_token('STRING', '\'([^\'\\\\]+|\\\\.)*\'');
lexer_factory.add_token('INTEGER', '[+-]?(0|[1-9][0-9]*)');
Lexer = lexer_factory.create_class()

# AST nodes
AstBaseClass = ast.create_base_node('AstBaseClass')
class AlpScript(AstBaseClass):
    property_definitions = (
        ast.Property('head', klass=0),
        ast.Property('body', klass=0),
    )

def AlpHead(**kwargs):
    body = kwargs.pop('body', ())

    if 'head' in kwargs:
        head = kwargs.pop('head')
        body = (head,) + body

    if 'tail' in kwargs:
        tail = kwargs.pop('tail')
        body = body + (tail,)

    return body

class AlpHeaderEntry(AstBaseClass):
    property_definitions = (
        ast.Property('key', klass=0),
        ast.Property('value', klass=0),
    )

def AlpBody(**kwargs):
    body = kwargs.pop('body', ())

    if 'head' in kwargs:
        head = kwargs.pop('head')
        body = (head,) + body

    if 'tail' in kwargs:
        tail = kwargs.pop('tail')
        body = body + (tail,)

    return body

# Helper class for selectors!
def SelMainEntry(arg):
    return arg

class AlpImport(AstBaseClass):
    property_definitions = (
        ast.Property('import_from', klass=0),
        ast.Property('import_name', klass=0),
        ast.Property('import_as', klass=1),
    )

class AlpStart(AstBaseClass):
    property_definitions = (
        ast.Property('symbol', klass=0),
    )

# Helper class for selectors!
def SelToken(arg):
    return arg

class AlpToken(AstBaseClass):
    property_definitions = (
        ast.Property('name', klass=0),
        ast.Property('value', klass=0),
    )

class AlpLiteral(AstBaseClass):
    property_definitions = (
        ast.Property('name', klass=0),
        ast.Property('value', klass=0),
    )

class AlpKeyword(AstBaseClass):
    property_definitions = (
        ast.Property('value', klass=0),
    )

class AlpIgnore(AstBaseClass):
    property_definitions = (
        ast.Property('name', klass=0),
        ast.Property('value', klass=0),
    )

# Helper class for selectors!
def SelParser(arg):
    return arg

class AlpPrecedence(AstBaseClass):
    property_definitions = (
        ast.Property('direction', klass=0),
        ast.Property('tokens', klass=0),
    )

class AlpNode(AstBaseClass):
    property_definitions = (
        ast.Property('name', klass=0),
        ast.Property('body', klass=0),
    )

class AlpList(AstBaseClass):
    property_definitions = (
        ast.Property('name', klass=0),
        ast.Property('body', klass=0),
    )

class AlpSelection(AstBaseClass):
    property_definitions = (
        ast.Property('name', klass=0),
        ast.Property('body', klass=0),
    )

class AlpNodeBody(AstBaseClass):
    property_definitions = (
        ast.Property('properties', klass=0),
        ast.Property('rules', klass=0),
    )

def AlpPropertyList(**kwargs):
    body = kwargs.pop('body', ())

    if 'head' in kwargs:
        head = kwargs.pop('head')
        body = (head,) + body

    if 'tail' in kwargs:
        tail = kwargs.pop('tail')
        body = body + (tail,)

    return body

class AlpProperty(AstBaseClass):
    property_definitions = (
        ast.Property('klass', klass=0),
        ast.Property('name', klass=0),
    )

def AlpRuleList(**kwargs):
    body = kwargs.pop('body', ())

    if 'head' in kwargs:
        head = kwargs.pop('head')
        body = (head,) + body

    if 'tail' in kwargs:
        tail = kwargs.pop('tail')
        body = body + (tail,)

    return body

class AlpRule(AstBaseClass):
    property_definitions = (
        ast.Property('entries', klass=0),
        ast.Property('precsymbol', klass=1),
    )

def AlpRuleEntryList(**kwargs):
    body = kwargs.pop('body', ())

    if 'head' in kwargs:
        head = kwargs.pop('head')
        body = (head,) + body

    if 'tail' in kwargs:
        tail = kwargs.pop('tail')
        body = body + (tail,)

    return body

class AlpRuleEntry(AstBaseClass):
    property_definitions = (
        ast.Property('ignored', klass=1),
        ast.Property('key', klass=1),
        ast.Property('name', klass=0),
    )

def AlpModuleName(**kwargs):
    body = kwargs.pop('body', ())

    if 'head' in kwargs:
        head = kwargs.pop('head')
        body = (head,) + body

    if 'tail' in kwargs:
        tail = kwargs.pop('tail')
        body = body + (tail,)

    return body

def AlpIdList(**kwargs):
    body = kwargs.pop('body', ())

    if 'head' in kwargs:
        head = kwargs.pop('head')
        body = (head,) + body

    if 'tail' in kwargs:
        tail = kwargs.pop('tail')
        body = body + (tail,)

    return body


# Parser
class Parser(ParserBase):
    start = 'AlpScript'

    
    # Rules for node AlpScript
    rule_AlpScript_0 = rule.Rule('AlpScript', rule.RuleEntry('AlpHead', key='head', ignore=None), rule.RuleEntry('AlpBody', key='body', ignore=None))
    def p_AlpScript_0(self, p):
        p[0] = self.rule_AlpScript_0(AlpScript, p[1:])
    p_AlpScript_0.__doc__ = rule_AlpScript_0.to_yacc_rule()


    # Rules for node AlpHead
    rule_AlpHead_0 = rule.Rule('AlpHead')
    def p_AlpHead_0(self, p):
        p[0] = self.rule_AlpHead_0(AlpHead, p[1:])
    p_AlpHead_0.__doc__ = rule_AlpHead_0.to_yacc_rule()

    rule_AlpHead_1 = rule.Rule('AlpHead', rule.RuleEntry('AlpHeaderEntry', key='head', ignore=None), rule.RuleEntry('SEMICOLON', key=None, ignore='-'), rule.RuleEntry('AlpHead', key='body', ignore=None))
    def p_AlpHead_1(self, p):
        p[0] = self.rule_AlpHead_1(AlpHead, p[1:])
    p_AlpHead_1.__doc__ = rule_AlpHead_1.to_yacc_rule()


    # Rules for node AlpHeaderEntry
    rule_AlpHeaderEntry_0 = rule.Rule('AlpHeaderEntry', rule.RuleEntry('LANGUAGE', key=None, ignore=None), rule.RuleEntry('ID', key=None, ignore=None))
    def p_AlpHeaderEntry_0(self, p):
        p[0] = self.rule_AlpHeaderEntry_0(AlpHeaderEntry, p[1:])
    p_AlpHeaderEntry_0.__doc__ = rule_AlpHeaderEntry_0.to_yacc_rule()

    rule_AlpHeaderEntry_1 = rule.Rule('AlpHeaderEntry', rule.RuleEntry('AUTHOR', key=None, ignore=None), rule.RuleEntry('STRING', key=None, ignore=None))
    def p_AlpHeaderEntry_1(self, p):
        p[0] = self.rule_AlpHeaderEntry_1(AlpHeaderEntry, p[1:])
    p_AlpHeaderEntry_1.__doc__ = rule_AlpHeaderEntry_1.to_yacc_rule()

    rule_AlpHeaderEntry_2 = rule.Rule('AlpHeaderEntry', rule.RuleEntry('EMAIL', key=None, ignore=None), rule.RuleEntry('STRING', key=None, ignore=None))
    def p_AlpHeaderEntry_2(self, p):
        p[0] = self.rule_AlpHeaderEntry_2(AlpHeaderEntry, p[1:])
    p_AlpHeaderEntry_2.__doc__ = rule_AlpHeaderEntry_2.to_yacc_rule()

    rule_AlpHeaderEntry_3 = rule.Rule('AlpHeaderEntry', rule.RuleEntry('VERSION', key=None, ignore=None), rule.RuleEntry('INTEGER', key=None, ignore=None))
    def p_AlpHeaderEntry_3(self, p):
        p[0] = self.rule_AlpHeaderEntry_3(AlpHeaderEntry, p[1:])
    p_AlpHeaderEntry_3.__doc__ = rule_AlpHeaderEntry_3.to_yacc_rule()


    # Rules for node AlpBody
    rule_AlpBody_0 = rule.Rule('AlpBody')
    def p_AlpBody_0(self, p):
        p[0] = self.rule_AlpBody_0(AlpBody, p[1:])
    p_AlpBody_0.__doc__ = rule_AlpBody_0.to_yacc_rule()

    rule_AlpBody_1 = rule.Rule('AlpBody', rule.RuleEntry('SelMainEntry', key='head', ignore=None), rule.RuleEntry('SEMICOLON', key=None, ignore='-'), rule.RuleEntry('AlpBody', key='body', ignore=None))
    def p_AlpBody_1(self, p):
        p[0] = self.rule_AlpBody_1(AlpBody, p[1:])
    p_AlpBody_1.__doc__ = rule_AlpBody_1.to_yacc_rule()


    # Rules for node SelMainEntry
    rule_SelMainEntry_0 = rule.Rule('SelMainEntry', rule.RuleEntry('AlpImport', key=None, ignore=None))
    def p_SelMainEntry_0(self, p):
        p[0] = self.rule_SelMainEntry_0(SelMainEntry, p[1:])
    p_SelMainEntry_0.__doc__ = rule_SelMainEntry_0.to_yacc_rule()

    rule_SelMainEntry_1 = rule.Rule('SelMainEntry', rule.RuleEntry('AlpStart', key=None, ignore=None))
    def p_SelMainEntry_1(self, p):
        p[0] = self.rule_SelMainEntry_1(SelMainEntry, p[1:])
    p_SelMainEntry_1.__doc__ = rule_SelMainEntry_1.to_yacc_rule()

    rule_SelMainEntry_2 = rule.Rule('SelMainEntry', rule.RuleEntry('SelToken', key=None, ignore=None))
    def p_SelMainEntry_2(self, p):
        p[0] = self.rule_SelMainEntry_2(SelMainEntry, p[1:])
    p_SelMainEntry_2.__doc__ = rule_SelMainEntry_2.to_yacc_rule()

    rule_SelMainEntry_3 = rule.Rule('SelMainEntry', rule.RuleEntry('SelParser', key=None, ignore=None))
    def p_SelMainEntry_3(self, p):
        p[0] = self.rule_SelMainEntry_3(SelMainEntry, p[1:])
    p_SelMainEntry_3.__doc__ = rule_SelMainEntry_3.to_yacc_rule()


    # Rules for node AlpImport
    rule_AlpImport_0 = rule.Rule('AlpImport', rule.RuleEntry('FROM', key=None, ignore='-'), rule.RuleEntry('AlpModuleName', key=None, ignore=None), rule.RuleEntry('IMPORT', key=None, ignore='-'), rule.RuleEntry('ID', key=None, ignore=None))
    def p_AlpImport_0(self, p):
        p[0] = self.rule_AlpImport_0(AlpImport, p[1:])
    p_AlpImport_0.__doc__ = rule_AlpImport_0.to_yacc_rule()

    rule_AlpImport_1 = rule.Rule('AlpImport', rule.RuleEntry('FROM', key=None, ignore='-'), rule.RuleEntry('AlpModuleName', key=None, ignore=None), rule.RuleEntry('IMPORT', key=None, ignore='-'), rule.RuleEntry('ID', key=None, ignore=None), rule.RuleEntry('AS', key=None, ignore='-'), rule.RuleEntry('ID', key=None, ignore=None))
    def p_AlpImport_1(self, p):
        p[0] = self.rule_AlpImport_1(AlpImport, p[1:])
    p_AlpImport_1.__doc__ = rule_AlpImport_1.to_yacc_rule()


    # Rules for node AlpStart
    rule_AlpStart_0 = rule.Rule('AlpStart', rule.RuleEntry('START', key=None, ignore='-'), rule.RuleEntry('ID', key=None, ignore=None))
    def p_AlpStart_0(self, p):
        p[0] = self.rule_AlpStart_0(AlpStart, p[1:])
    p_AlpStart_0.__doc__ = rule_AlpStart_0.to_yacc_rule()


    # Rules for node SelToken
    rule_SelToken_0 = rule.Rule('SelToken', rule.RuleEntry('AlpToken', key=None, ignore=None))
    def p_SelToken_0(self, p):
        p[0] = self.rule_SelToken_0(SelToken, p[1:])
    p_SelToken_0.__doc__ = rule_SelToken_0.to_yacc_rule()

    rule_SelToken_1 = rule.Rule('SelToken', rule.RuleEntry('AlpLiteral', key=None, ignore=None))
    def p_SelToken_1(self, p):
        p[0] = self.rule_SelToken_1(SelToken, p[1:])
    p_SelToken_1.__doc__ = rule_SelToken_1.to_yacc_rule()

    rule_SelToken_2 = rule.Rule('SelToken', rule.RuleEntry('AlpKeyword', key=None, ignore=None))
    def p_SelToken_2(self, p):
        p[0] = self.rule_SelToken_2(SelToken, p[1:])
    p_SelToken_2.__doc__ = rule_SelToken_2.to_yacc_rule()

    rule_SelToken_3 = rule.Rule('SelToken', rule.RuleEntry('AlpIgnore', key=None, ignore=None))
    def p_SelToken_3(self, p):
        p[0] = self.rule_SelToken_3(SelToken, p[1:])
    p_SelToken_3.__doc__ = rule_SelToken_3.to_yacc_rule()


    # Rules for node AlpToken
    rule_AlpToken_0 = rule.Rule('AlpToken', rule.RuleEntry('TOKEN', key=None, ignore='-'), rule.RuleEntry('ID', key=None, ignore=None), rule.RuleEntry('STRING', key=None, ignore=None))
    def p_AlpToken_0(self, p):
        p[0] = self.rule_AlpToken_0(AlpToken, p[1:])
    p_AlpToken_0.__doc__ = rule_AlpToken_0.to_yacc_rule()


    # Rules for node AlpLiteral
    rule_AlpLiteral_0 = rule.Rule('AlpLiteral', rule.RuleEntry('LITERAL', key=None, ignore='-'), rule.RuleEntry('ID', key=None, ignore=None), rule.RuleEntry('STRING', key=None, ignore=None))
    def p_AlpLiteral_0(self, p):
        p[0] = self.rule_AlpLiteral_0(AlpLiteral, p[1:])
    p_AlpLiteral_0.__doc__ = rule_AlpLiteral_0.to_yacc_rule()


    # Rules for node AlpKeyword
    rule_AlpKeyword_0 = rule.Rule('AlpKeyword', rule.RuleEntry('KEYWORD', key=None, ignore='-'), rule.RuleEntry('ID', key=None, ignore=None))
    def p_AlpKeyword_0(self, p):
        p[0] = self.rule_AlpKeyword_0(AlpKeyword, p[1:])
    p_AlpKeyword_0.__doc__ = rule_AlpKeyword_0.to_yacc_rule()


    # Rules for node AlpIgnore
    rule_AlpIgnore_0 = rule.Rule('AlpIgnore', rule.RuleEntry('IGNORE', key=None, ignore='-'), rule.RuleEntry('ID', key=None, ignore=None), rule.RuleEntry('STRING', key=None, ignore=None))
    def p_AlpIgnore_0(self, p):
        p[0] = self.rule_AlpIgnore_0(AlpIgnore, p[1:])
    p_AlpIgnore_0.__doc__ = rule_AlpIgnore_0.to_yacc_rule()


    # Rules for node SelParser
    rule_SelParser_0 = rule.Rule('SelParser', rule.RuleEntry('AlpPrecedence', key=None, ignore=None))
    def p_SelParser_0(self, p):
        p[0] = self.rule_SelParser_0(SelParser, p[1:])
    p_SelParser_0.__doc__ = rule_SelParser_0.to_yacc_rule()

    rule_SelParser_1 = rule.Rule('SelParser', rule.RuleEntry('AlpNode', key=None, ignore=None))
    def p_SelParser_1(self, p):
        p[0] = self.rule_SelParser_1(SelParser, p[1:])
    p_SelParser_1.__doc__ = rule_SelParser_1.to_yacc_rule()

    rule_SelParser_2 = rule.Rule('SelParser', rule.RuleEntry('AlpList', key=None, ignore=None))
    def p_SelParser_2(self, p):
        p[0] = self.rule_SelParser_2(SelParser, p[1:])
    p_SelParser_2.__doc__ = rule_SelParser_2.to_yacc_rule()

    rule_SelParser_3 = rule.Rule('SelParser', rule.RuleEntry('AlpSelection', key=None, ignore=None))
    def p_SelParser_3(self, p):
        p[0] = self.rule_SelParser_3(SelParser, p[1:])
    p_SelParser_3.__doc__ = rule_SelParser_3.to_yacc_rule()


    # Rules for node AlpPrecedence
    rule_AlpPrecedence_0 = rule.Rule('AlpPrecedence', rule.RuleEntry('PRECEDENCE', key=None, ignore='-'), rule.RuleEntry('LEFT', key=None, ignore=None), rule.RuleEntry('LPAREN', key=None, ignore='-'), rule.RuleEntry('AlpIdList', key=None, ignore=None), rule.RuleEntry('RPAREN', key=None, ignore='-'))
    def p_AlpPrecedence_0(self, p):
        p[0] = self.rule_AlpPrecedence_0(AlpPrecedence, p[1:])
    p_AlpPrecedence_0.__doc__ = rule_AlpPrecedence_0.to_yacc_rule()

    rule_AlpPrecedence_1 = rule.Rule('AlpPrecedence', rule.RuleEntry('PRECEDENCE', key=None, ignore='-'), rule.RuleEntry('RIGHT', key=None, ignore=None), rule.RuleEntry('LPAREN', key=None, ignore='-'), rule.RuleEntry('AlpIdList', key=None, ignore=None), rule.RuleEntry('RPAREN', key=None, ignore='-'))
    def p_AlpPrecedence_1(self, p):
        p[0] = self.rule_AlpPrecedence_1(AlpPrecedence, p[1:])
    p_AlpPrecedence_1.__doc__ = rule_AlpPrecedence_1.to_yacc_rule()


    # Rules for node AlpNode
    rule_AlpNode_0 = rule.Rule('AlpNode', rule.RuleEntry('NODE', key=None, ignore='-'), rule.RuleEntry('ID', key=None, ignore=None), rule.RuleEntry('LCURLY', key=None, ignore='-'), rule.RuleEntry('AlpNodeBody', key=None, ignore=None), rule.RuleEntry('RCURLY', key=None, ignore='-'))
    def p_AlpNode_0(self, p):
        p[0] = self.rule_AlpNode_0(AlpNode, p[1:])
    p_AlpNode_0.__doc__ = rule_AlpNode_0.to_yacc_rule()


    # Rules for node AlpList
    rule_AlpList_0 = rule.Rule('AlpList', rule.RuleEntry('LIST', key=None, ignore='-'), rule.RuleEntry('ID', key=None, ignore=None), rule.RuleEntry('LCURLY', key=None, ignore='-'), rule.RuleEntry('AlpRuleList', key=None, ignore=None), rule.RuleEntry('RCURLY', key=None, ignore='-'))
    def p_AlpList_0(self, p):
        p[0] = self.rule_AlpList_0(AlpList, p[1:])
    p_AlpList_0.__doc__ = rule_AlpList_0.to_yacc_rule()


    # Rules for node AlpSelection
    rule_AlpSelection_0 = rule.Rule('AlpSelection', rule.RuleEntry('SELECTION', key=None, ignore='-'), rule.RuleEntry('ID', key=None, ignore=None), rule.RuleEntry('LCURLY', key=None, ignore='-'), rule.RuleEntry('AlpRuleList', key=None, ignore=None), rule.RuleEntry('RCURLY', key=None, ignore='-'))
    def p_AlpSelection_0(self, p):
        p[0] = self.rule_AlpSelection_0(AlpSelection, p[1:])
    p_AlpSelection_0.__doc__ = rule_AlpSelection_0.to_yacc_rule()


    # Rules for node AlpNodeBody
    rule_AlpNodeBody_0 = rule.Rule('AlpNodeBody', rule.RuleEntry('AlpPropertyList', key=None, ignore=None), rule.RuleEntry('AlpRuleList', key=None, ignore=None))
    def p_AlpNodeBody_0(self, p):
        p[0] = self.rule_AlpNodeBody_0(AlpNodeBody, p[1:])
    p_AlpNodeBody_0.__doc__ = rule_AlpNodeBody_0.to_yacc_rule()


    # Rules for node AlpPropertyList
    rule_AlpPropertyList_0 = rule.Rule('AlpPropertyList')
    def p_AlpPropertyList_0(self, p):
        p[0] = self.rule_AlpPropertyList_0(AlpPropertyList, p[1:])
    p_AlpPropertyList_0.__doc__ = rule_AlpPropertyList_0.to_yacc_rule()

    rule_AlpPropertyList_1 = rule.Rule('AlpPropertyList', rule.RuleEntry('AlpProperty', key='head', ignore=None), rule.RuleEntry('SEMICOLON', key=None, ignore='-'), rule.RuleEntry('AlpPropertyList', key='body', ignore=None))
    def p_AlpPropertyList_1(self, p):
        p[0] = self.rule_AlpPropertyList_1(AlpPropertyList, p[1:])
    p_AlpPropertyList_1.__doc__ = rule_AlpPropertyList_1.to_yacc_rule()


    # Rules for node AlpProperty
    rule_AlpProperty_0 = rule.Rule('AlpProperty', rule.RuleEntry('REQUIRED', key=None, ignore=None), rule.RuleEntry('ID', key=None, ignore=None))
    def p_AlpProperty_0(self, p):
        p[0] = self.rule_AlpProperty_0(AlpProperty, p[1:])
    p_AlpProperty_0.__doc__ = rule_AlpProperty_0.to_yacc_rule()

    rule_AlpProperty_1 = rule.Rule('AlpProperty', rule.RuleEntry('OPTIONAL', key=None, ignore=None), rule.RuleEntry('ID', key=None, ignore=None))
    def p_AlpProperty_1(self, p):
        p[0] = self.rule_AlpProperty_1(AlpProperty, p[1:])
    p_AlpProperty_1.__doc__ = rule_AlpProperty_1.to_yacc_rule()


    # Rules for node AlpRuleList
    rule_AlpRuleList_0 = rule.Rule('AlpRuleList', rule.RuleEntry('AlpRule', key='head', ignore=None), rule.RuleEntry('SEMICOLON', key=None, ignore='-'))
    def p_AlpRuleList_0(self, p):
        p[0] = self.rule_AlpRuleList_0(AlpRuleList, p[1:])
    p_AlpRuleList_0.__doc__ = rule_AlpRuleList_0.to_yacc_rule()

    rule_AlpRuleList_1 = rule.Rule('AlpRuleList', rule.RuleEntry('AlpRule', key='head', ignore=None), rule.RuleEntry('SEMICOLON', key=None, ignore='-'), rule.RuleEntry('AlpRuleList', key='body', ignore=None))
    def p_AlpRuleList_1(self, p):
        p[0] = self.rule_AlpRuleList_1(AlpRuleList, p[1:])
    p_AlpRuleList_1.__doc__ = rule_AlpRuleList_1.to_yacc_rule()


    # Rules for node AlpRule
    rule_AlpRule_0 = rule.Rule('AlpRule', rule.RuleEntry('RULE', key=None, ignore='-'), rule.RuleEntry('AlpRuleEntryList', key=None, ignore=None))
    def p_AlpRule_0(self, p):
        p[0] = self.rule_AlpRule_0(AlpRule, p[1:])
    p_AlpRule_0.__doc__ = rule_AlpRule_0.to_yacc_rule()

    rule_AlpRule_1 = rule.Rule('AlpRule', rule.RuleEntry('RULE', key=None, ignore='-'), rule.RuleEntry('AlpRuleEntryList', key=None, ignore=None), rule.RuleEntry('PRECSYM', key=None, ignore='-'), rule.RuleEntry('ID', key=None, ignore=None))
    def p_AlpRule_1(self, p):
        p[0] = self.rule_AlpRule_1(AlpRule, p[1:])
    p_AlpRule_1.__doc__ = rule_AlpRule_1.to_yacc_rule()


    # Rules for node AlpRuleEntryList
    rule_AlpRuleEntryList_0 = rule.Rule('AlpRuleEntryList')
    def p_AlpRuleEntryList_0(self, p):
        p[0] = self.rule_AlpRuleEntryList_0(AlpRuleEntryList, p[1:])
    p_AlpRuleEntryList_0.__doc__ = rule_AlpRuleEntryList_0.to_yacc_rule()

    rule_AlpRuleEntryList_1 = rule.Rule('AlpRuleEntryList', rule.RuleEntry('AlpRuleEntry', key='head', ignore=None), rule.RuleEntry('AlpRuleEntryList', key='body', ignore=None))
    def p_AlpRuleEntryList_1(self, p):
        p[0] = self.rule_AlpRuleEntryList_1(AlpRuleEntryList, p[1:])
    p_AlpRuleEntryList_1.__doc__ = rule_AlpRuleEntryList_1.to_yacc_rule()


    # Rules for node AlpRuleEntry
    rule_AlpRuleEntry_0 = rule.Rule('AlpRuleEntry', rule.RuleEntry('ID', key='name', ignore=None))
    def p_AlpRuleEntry_0(self, p):
        p[0] = self.rule_AlpRuleEntry_0(AlpRuleEntry, p[1:])
    p_AlpRuleEntry_0.__doc__ = rule_AlpRuleEntry_0.to_yacc_rule()

    rule_AlpRuleEntry_1 = rule.Rule('AlpRuleEntry', rule.RuleEntry('ID', key='key', ignore=None), rule.RuleEntry('EQ', key=None, ignore='-'), rule.RuleEntry('ID', key='name', ignore=None))
    def p_AlpRuleEntry_1(self, p):
        p[0] = self.rule_AlpRuleEntry_1(AlpRuleEntry, p[1:])
    p_AlpRuleEntry_1.__doc__ = rule_AlpRuleEntry_1.to_yacc_rule()

    rule_AlpRuleEntry_2 = rule.Rule('AlpRuleEntry', rule.RuleEntry('MINUS', key='ignored', ignore=None), rule.RuleEntry('ID', key='name', ignore=None))
    def p_AlpRuleEntry_2(self, p):
        p[0] = self.rule_AlpRuleEntry_2(AlpRuleEntry, p[1:])
    p_AlpRuleEntry_2.__doc__ = rule_AlpRuleEntry_2.to_yacc_rule()


    # Rules for node AlpModuleName
    rule_AlpModuleName_0 = rule.Rule('AlpModuleName', rule.RuleEntry('ID', key='head', ignore=None))
    def p_AlpModuleName_0(self, p):
        p[0] = self.rule_AlpModuleName_0(AlpModuleName, p[1:])
    p_AlpModuleName_0.__doc__ = rule_AlpModuleName_0.to_yacc_rule()

    rule_AlpModuleName_1 = rule.Rule('AlpModuleName', rule.RuleEntry('ID', key='head', ignore=None), rule.RuleEntry('PERIOD', key=None, ignore='-'), rule.RuleEntry('AlpModuleName', key='body', ignore=None))
    def p_AlpModuleName_1(self, p):
        p[0] = self.rule_AlpModuleName_1(AlpModuleName, p[1:])
    p_AlpModuleName_1.__doc__ = rule_AlpModuleName_1.to_yacc_rule()


    # Rules for node AlpIdList
    rule_AlpIdList_0 = rule.Rule('AlpIdList', rule.RuleEntry('ID', key='head', ignore=None))
    def p_AlpIdList_0(self, p):
        p[0] = self.rule_AlpIdList_0(AlpIdList, p[1:])
    p_AlpIdList_0.__doc__ = rule_AlpIdList_0.to_yacc_rule()

    rule_AlpIdList_1 = rule.Rule('AlpIdList', rule.RuleEntry('ID', key='head', ignore=None), rule.RuleEntry('COLON', key=None, ignore='-'), rule.RuleEntry('AlpIdList', key='body', ignore=None))
    def p_AlpIdList_1(self, p):
        p[0] = self.rule_AlpIdList_1(AlpIdList, p[1:])
    p_AlpIdList_1.__doc__ = rule_AlpIdList_1.to_yacc_rule()



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
