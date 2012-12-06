# THIS IS AN AUTOMATICALLY GENERATED FILE. ALL MANUAL MODIFICATIONS TO IT MAY
# BE LOST AT ANY TIME! MODIFY THE TEMPLATE INSTEAD (see below)
#
# Source file         alplang.alp
# Parser class        codega.alp.generator.ScriptParser
# Target file         script.py
# Generator class     codega.alp.generator.main_generator

__version__ = '2'
__language__ = 'alp'

__author__ = 'Hercinger Viktor'
__email__ = 'hercinger.viktor@gmail.com'

from codega.source import SourceBase

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
lexer_factory.add_ignore_token('SPACES', '\\s+');
lexer_factory.add_ignore_token('COMMENTS', '\\#.*?\\n');
lexer_factory.add_literal('FROM', 'from')
lexer_factory.add_literal('IMPORT', 'import')
lexer_factory.add_literal('AS', 'as')
lexer_factory.add_literal('TOKEN', 'token')
lexer_factory.add_literal('KEYWORD', 'keyword')
lexer_factory.add_literal('LITERAL', 'literal')
lexer_factory.add_literal('IGNORE', 'ignore')
lexer_factory.add_literal('NODE', 'node')
lexer_factory.add_literal('LIST', 'list')
lexer_factory.add_literal('SELECTION', 'selection')
lexer_factory.add_literal('OPTIONAL', 'optional')
lexer_factory.add_literal('REQUIRED', 'required')
lexer_factory.add_literal('RULE', 'rule')
lexer_factory.add_literal('START', 'start')
lexer_factory.add_literal('PRECEDENCE', 'precedence')
lexer_factory.add_literal('LEFT', 'left')
lexer_factory.add_literal('RIGHT', 'right')
lexer_factory.add_literal('LANGUAGE', 'language')
lexer_factory.add_literal('AUTHOR', 'author')
lexer_factory.add_literal('VERSION', 'version')
lexer_factory.add_literal('EMAIL', 'email')
lexer_factory.add_literal('SEMICOLON', ';')
lexer_factory.add_literal('COLON', ',')
lexer_factory.add_literal('MINUS', '-')
lexer_factory.add_literal('EQ', '=')
lexer_factory.add_literal('PERIOD', '.')
lexer_factory.add_literal('COMMA', ':')
lexer_factory.add_literal('LCURLY', '{')
lexer_factory.add_literal('RCURLY', '}')
lexer_factory.add_literal('LPAREN', '(')
lexer_factory.add_literal('RPAREN', ')')
lexer_factory.add_literal('PRECSYM', '%prec')
lexer_factory.add_literal('ERRSYM', '%error')
lexer_factory.add_literal('WARNSYM', '%warning')
lexer_factory.add_token('ID', '[a-zA-Z_][a-zA-Z0-9_]*')
lexer_factory.add_token('STRING', '\'([^\'\\\\]+|\\\\.)*\'')
lexer_factory.add_token('INTEGER', '[+-]?(0|[1-9][0-9]*)')
Lexer = lexer_factory.create_class()

# AST nodes
metainfo = ast.Metainfo()

AlpScript_properties = (
    ('head', ast.REQUIRED),
    ('body', ast.REQUIRED),
)
AlpScript_info = ast.Info('AlpScript', AlpScript_properties)
AlpScript = AlpScript_info.get_class(metainfo)

AlpHead_properties = (
  ('data', ast.REQUIRED),
)
AlpHead_info = ast.Info('AlpHead', AlpHead_properties, base=ast.AstList)
AlpHead = AlpHead_info.get_class(metainfo)

AlpHeaderEntry_properties = (
    ('key', ast.REQUIRED),
    ('value', ast.REQUIRED),
)
AlpHeaderEntry_info = ast.Info('AlpHeaderEntry', AlpHeaderEntry_properties)
AlpHeaderEntry = AlpHeaderEntry_info.get_class(metainfo)

AlpBody_properties = (
  ('data', ast.REQUIRED),
)
AlpBody_info = ast.Info('AlpBody', AlpBody_properties, base=ast.AstList)
AlpBody = AlpBody_info.get_class(metainfo)

# Helper class for selectors!
def SelMainEntry(arg):
    return arg

AlpImport_properties = (
    ('import_from', ast.OPTIONAL),
    ('import_name', ast.REQUIRED),
    ('import_as', ast.OPTIONAL),
)
AlpImport_info = ast.Info('AlpImport', AlpImport_properties)
AlpImport = AlpImport_info.get_class(metainfo)

AlpStart_properties = (
    ('symbol', ast.REQUIRED),
)
AlpStart_info = ast.Info('AlpStart', AlpStart_properties)
AlpStart = AlpStart_info.get_class(metainfo)

# Helper class for selectors!
def SelToken(arg):
    return arg

AlpToken_properties = (
    ('name', ast.REQUIRED),
    ('value', ast.REQUIRED),
    ('metainfo', ast.REQUIRED),
)
AlpToken_info = ast.Info('AlpToken', AlpToken_properties)
AlpToken = AlpToken_info.get_class(metainfo)

AlpLiteral_properties = (
    ('name', ast.REQUIRED),
    ('value', ast.REQUIRED),
    ('metainfo', ast.REQUIRED),
)
AlpLiteral_info = ast.Info('AlpLiteral', AlpLiteral_properties)
AlpLiteral = AlpLiteral_info.get_class(metainfo)

AlpKeyword_properties = (
    ('value', ast.REQUIRED),
)
AlpKeyword_info = ast.Info('AlpKeyword', AlpKeyword_properties)
AlpKeyword = AlpKeyword_info.get_class(metainfo)

AlpIgnore_properties = (
    ('name', ast.REQUIRED),
    ('value', ast.REQUIRED),
)
AlpIgnore_info = ast.Info('AlpIgnore', AlpIgnore_properties)
AlpIgnore = AlpIgnore_info.get_class(metainfo)

# Helper class for selectors!
def SelParser(arg):
    return arg

AlpPrecedence_properties = (
    ('direction', ast.REQUIRED),
    ('tokens', ast.REQUIRED),
)
AlpPrecedence_info = ast.Info('AlpPrecedence', AlpPrecedence_properties)
AlpPrecedence = AlpPrecedence_info.get_class(metainfo)

AlpNode_properties = (
    ('name', ast.REQUIRED),
    ('body', ast.REQUIRED),
)
AlpNode_info = ast.Info('AlpNode', AlpNode_properties)
AlpNode = AlpNode_info.get_class(metainfo)

AlpList_properties = (
    ('name', ast.REQUIRED),
    ('body', ast.REQUIRED),
)
AlpList_info = ast.Info('AlpList', AlpList_properties)
AlpList = AlpList_info.get_class(metainfo)

AlpSelection_properties = (
    ('name', ast.REQUIRED),
    ('body', ast.REQUIRED),
)
AlpSelection_info = ast.Info('AlpSelection', AlpSelection_properties)
AlpSelection = AlpSelection_info.get_class(metainfo)

AlpNodeBody_properties = (
    ('properties', ast.REQUIRED),
    ('rules', ast.REQUIRED),
)
AlpNodeBody_info = ast.Info('AlpNodeBody', AlpNodeBody_properties)
AlpNodeBody = AlpNodeBody_info.get_class(metainfo)

AlpPropertyList_properties = (
  ('data', ast.REQUIRED),
)
AlpPropertyList_info = ast.Info('AlpPropertyList', AlpPropertyList_properties, base=ast.AstList)
AlpPropertyList = AlpPropertyList_info.get_class(metainfo)

AlpProperty_properties = (
    ('klass', ast.REQUIRED),
    ('name', ast.REQUIRED),
)
AlpProperty_info = ast.Info('AlpProperty', AlpProperty_properties)
AlpProperty = AlpProperty_info.get_class(metainfo)

AlpRuleList_properties = (
  ('data', ast.REQUIRED),
)
AlpRuleList_info = ast.Info('AlpRuleList', AlpRuleList_properties, base=ast.AstList)
AlpRuleList = AlpRuleList_info.get_class(metainfo)

AlpRule_properties = (
    ('entries', ast.REQUIRED),
    ('metainfo', ast.REQUIRED),
)
AlpRule_info = ast.Info('AlpRule', AlpRule_properties)
AlpRule = AlpRule_info.get_class(metainfo)

AlpRuleEntryList_properties = (
  ('data', ast.REQUIRED),
)
AlpRuleEntryList_info = ast.Info('AlpRuleEntryList', AlpRuleEntryList_properties, base=ast.AstList)
AlpRuleEntryList = AlpRuleEntryList_info.get_class(metainfo)

AlpRuleEntry_properties = (
    ('ignored', ast.OPTIONAL),
    ('key', ast.OPTIONAL),
    ('name', ast.REQUIRED),
)
AlpRuleEntry_info = ast.Info('AlpRuleEntry', AlpRuleEntry_properties)
AlpRuleEntry = AlpRuleEntry_info.get_class(metainfo)

AlpModuleName_properties = (
  ('data', ast.REQUIRED),
)
AlpModuleName_info = ast.Info('AlpModuleName', AlpModuleName_properties, base=ast.AstList)
AlpModuleName = AlpModuleName_info.get_class(metainfo)

AlpIdList_properties = (
  ('data', ast.REQUIRED),
)
AlpIdList_info = ast.Info('AlpIdList', AlpIdList_properties, base=ast.AstList)
AlpIdList = AlpIdList_info.get_class(metainfo)

AlpRuleMetainfoList_properties = (
  ('data', ast.REQUIRED),
)
AlpRuleMetainfoList_info = ast.Info('AlpRuleMetainfoList', AlpRuleMetainfoList_properties, base=ast.AstList)
AlpRuleMetainfoList = AlpRuleMetainfoList_info.get_class(metainfo)

AlpTokenMetainfoList_properties = (
  ('data', ast.REQUIRED),
)
AlpTokenMetainfoList_info = ast.Info('AlpTokenMetainfoList', AlpTokenMetainfoList_properties, base=ast.AstList)
AlpTokenMetainfoList = AlpTokenMetainfoList_info.get_class(metainfo)

# Helper class for selectors!
def AlpRuleMetainfo(arg):
    return arg

# Helper class for selectors!
def AlpTokenMetainfo(arg):
    return arg

AlpPrecedenceMetainfo_properties = (
    ('prec', ast.REQUIRED),
)
AlpPrecedenceMetainfo_info = ast.Info('AlpPrecedenceMetainfo', AlpPrecedenceMetainfo_properties)
AlpPrecedenceMetainfo = AlpPrecedenceMetainfo_info.get_class(metainfo)

AlpErrorMetainfo_properties = (
    ('message_format', ast.REQUIRED),
)
AlpErrorMetainfo_info = ast.Info('AlpErrorMetainfo', AlpErrorMetainfo_properties)
AlpErrorMetainfo = AlpErrorMetainfo_info.get_class(metainfo)

AlpWarningMetainfo_properties = (
    ('message_format', ast.REQUIRED),
)
AlpWarningMetainfo_info = ast.Info('AlpWarningMetainfo', AlpWarningMetainfo_properties)
AlpWarningMetainfo = AlpWarningMetainfo_info.get_class(metainfo)


# Parser
class Parser(ParserBase):
    start = 'AlpScript'

    
    # Rules for node AlpScript
    rule_AlpScript_0 = rule.Rule('AlpScript', rule.RuleEntry('AlpHead', key='head', ignore=None), rule.RuleEntry('AlpBody', key='body', ignore=None))
    def p_AlpScript_0(self, p):
        p[0] = self.rule_AlpScript_0(AlpScript, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpScript_0.__doc__ = rule_AlpScript_0.to_yacc_rule()


    # Rules for node AlpHead
    rule_AlpHead_0 = rule.Rule('AlpHead')
    def p_AlpHead_0(self, p):
        p[0] = self.rule_AlpHead_0(AlpHead, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpHead_0.__doc__ = rule_AlpHead_0.to_yacc_rule()

    rule_AlpHead_1 = rule.Rule('AlpHead', rule.RuleEntry('AlpHeaderEntry', key='head', ignore=None), rule.RuleEntry('SEMICOLON', key=None, ignore='-'), rule.RuleEntry('AlpHead', key='body', ignore=None))
    def p_AlpHead_1(self, p):
        p[0] = self.rule_AlpHead_1(AlpHead, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpHead_1.__doc__ = rule_AlpHead_1.to_yacc_rule()


    # Rules for node AlpHeaderEntry
    rule_AlpHeaderEntry_0 = rule.Rule('AlpHeaderEntry', rule.RuleEntry('LANGUAGE', key=None, ignore=None), rule.RuleEntry('ID', key=None, ignore=None))
    def p_AlpHeaderEntry_0(self, p):
        p[0] = self.rule_AlpHeaderEntry_0(AlpHeaderEntry, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpHeaderEntry_0.__doc__ = rule_AlpHeaderEntry_0.to_yacc_rule()

    rule_AlpHeaderEntry_1 = rule.Rule('AlpHeaderEntry', rule.RuleEntry('AUTHOR', key=None, ignore=None), rule.RuleEntry('STRING', key=None, ignore=None))
    def p_AlpHeaderEntry_1(self, p):
        p[0] = self.rule_AlpHeaderEntry_1(AlpHeaderEntry, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpHeaderEntry_1.__doc__ = rule_AlpHeaderEntry_1.to_yacc_rule()

    rule_AlpHeaderEntry_2 = rule.Rule('AlpHeaderEntry', rule.RuleEntry('EMAIL', key=None, ignore=None), rule.RuleEntry('STRING', key=None, ignore=None))
    def p_AlpHeaderEntry_2(self, p):
        p[0] = self.rule_AlpHeaderEntry_2(AlpHeaderEntry, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpHeaderEntry_2.__doc__ = rule_AlpHeaderEntry_2.to_yacc_rule()

    rule_AlpHeaderEntry_3 = rule.Rule('AlpHeaderEntry', rule.RuleEntry('VERSION', key=None, ignore=None), rule.RuleEntry('INTEGER', key=None, ignore=None))
    def p_AlpHeaderEntry_3(self, p):
        p[0] = self.rule_AlpHeaderEntry_3(AlpHeaderEntry, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpHeaderEntry_3.__doc__ = rule_AlpHeaderEntry_3.to_yacc_rule()


    # Rules for node AlpBody
    rule_AlpBody_0 = rule.Rule('AlpBody')
    def p_AlpBody_0(self, p):
        p[0] = self.rule_AlpBody_0(AlpBody, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpBody_0.__doc__ = rule_AlpBody_0.to_yacc_rule()

    rule_AlpBody_1 = rule.Rule('AlpBody', rule.RuleEntry('SelMainEntry', key='head', ignore=None), rule.RuleEntry('SEMICOLON', key=None, ignore='-'), rule.RuleEntry('AlpBody', key='body', ignore=None))
    def p_AlpBody_1(self, p):
        p[0] = self.rule_AlpBody_1(AlpBody, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpBody_1.__doc__ = rule_AlpBody_1.to_yacc_rule()


    # Rules for node SelMainEntry
    rule_SelMainEntry_0 = rule.Rule('SelMainEntry', rule.RuleEntry('AlpImport', key=None, ignore=None))
    def p_SelMainEntry_0(self, p):
        p[0] = self.rule_SelMainEntry_0(SelMainEntry, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_SelMainEntry_0.__doc__ = rule_SelMainEntry_0.to_yacc_rule()

    rule_SelMainEntry_1 = rule.Rule('SelMainEntry', rule.RuleEntry('AlpStart', key=None, ignore=None))
    def p_SelMainEntry_1(self, p):
        p[0] = self.rule_SelMainEntry_1(SelMainEntry, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_SelMainEntry_1.__doc__ = rule_SelMainEntry_1.to_yacc_rule()

    rule_SelMainEntry_2 = rule.Rule('SelMainEntry', rule.RuleEntry('SelToken', key=None, ignore=None))
    def p_SelMainEntry_2(self, p):
        p[0] = self.rule_SelMainEntry_2(SelMainEntry, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_SelMainEntry_2.__doc__ = rule_SelMainEntry_2.to_yacc_rule()

    rule_SelMainEntry_3 = rule.Rule('SelMainEntry', rule.RuleEntry('SelParser', key=None, ignore=None))
    def p_SelMainEntry_3(self, p):
        p[0] = self.rule_SelMainEntry_3(SelMainEntry, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_SelMainEntry_3.__doc__ = rule_SelMainEntry_3.to_yacc_rule()


    # Rules for node AlpImport
    rule_AlpImport_0 = rule.Rule('AlpImport', rule.RuleEntry('IMPORT', key=None, ignore='-'), rule.RuleEntry('AlpModuleName', key='import_name', ignore=None))
    def p_AlpImport_0(self, p):
        p[0] = self.rule_AlpImport_0(AlpImport, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpImport_0.__doc__ = rule_AlpImport_0.to_yacc_rule()

    rule_AlpImport_1 = rule.Rule('AlpImport', rule.RuleEntry('IMPORT', key=None, ignore='-'), rule.RuleEntry('AlpModuleName', key='import_name', ignore=None), rule.RuleEntry('AS', key=None, ignore='-'), rule.RuleEntry('ID', key='import_as', ignore=None))
    def p_AlpImport_1(self, p):
        p[0] = self.rule_AlpImport_1(AlpImport, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpImport_1.__doc__ = rule_AlpImport_1.to_yacc_rule()

    rule_AlpImport_2 = rule.Rule('AlpImport', rule.RuleEntry('FROM', key=None, ignore='-'), rule.RuleEntry('AlpModuleName', key='import_from', ignore=None), rule.RuleEntry('IMPORT', key=None, ignore='-'), rule.RuleEntry('ID', key='import_name', ignore=None))
    def p_AlpImport_2(self, p):
        p[0] = self.rule_AlpImport_2(AlpImport, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpImport_2.__doc__ = rule_AlpImport_2.to_yacc_rule()

    rule_AlpImport_3 = rule.Rule('AlpImport', rule.RuleEntry('FROM', key=None, ignore='-'), rule.RuleEntry('AlpModuleName', key='import_from', ignore=None), rule.RuleEntry('IMPORT', key=None, ignore='-'), rule.RuleEntry('ID', key='import_name', ignore=None), rule.RuleEntry('AS', key=None, ignore='-'), rule.RuleEntry('ID', key='import_as', ignore=None))
    def p_AlpImport_3(self, p):
        p[0] = self.rule_AlpImport_3(AlpImport, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpImport_3.__doc__ = rule_AlpImport_3.to_yacc_rule()


    # Rules for node AlpStart
    rule_AlpStart_0 = rule.Rule('AlpStart', rule.RuleEntry('START', key=None, ignore='-'), rule.RuleEntry('ID', key=None, ignore=None))
    def p_AlpStart_0(self, p):
        p[0] = self.rule_AlpStart_0(AlpStart, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpStart_0.__doc__ = rule_AlpStart_0.to_yacc_rule()


    # Rules for node SelToken
    rule_SelToken_0 = rule.Rule('SelToken', rule.RuleEntry('AlpToken', key=None, ignore=None))
    def p_SelToken_0(self, p):
        p[0] = self.rule_SelToken_0(SelToken, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_SelToken_0.__doc__ = rule_SelToken_0.to_yacc_rule()

    rule_SelToken_1 = rule.Rule('SelToken', rule.RuleEntry('AlpLiteral', key=None, ignore=None))
    def p_SelToken_1(self, p):
        p[0] = self.rule_SelToken_1(SelToken, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_SelToken_1.__doc__ = rule_SelToken_1.to_yacc_rule()

    rule_SelToken_2 = rule.Rule('SelToken', rule.RuleEntry('AlpKeyword', key=None, ignore=None))
    def p_SelToken_2(self, p):
        p[0] = self.rule_SelToken_2(SelToken, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_SelToken_2.__doc__ = rule_SelToken_2.to_yacc_rule()

    rule_SelToken_3 = rule.Rule('SelToken', rule.RuleEntry('AlpIgnore', key=None, ignore=None))
    def p_SelToken_3(self, p):
        p[0] = self.rule_SelToken_3(SelToken, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_SelToken_3.__doc__ = rule_SelToken_3.to_yacc_rule()


    # Rules for node AlpToken
    rule_AlpToken_0 = rule.Rule('AlpToken', rule.RuleEntry('TOKEN', key=None, ignore='-'), rule.RuleEntry('ID', key=None, ignore=None), rule.RuleEntry('STRING', key=None, ignore=None), rule.RuleEntry('AlpTokenMetainfoList', key=None, ignore=None))
    def p_AlpToken_0(self, p):
        p[0] = self.rule_AlpToken_0(AlpToken, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpToken_0.__doc__ = rule_AlpToken_0.to_yacc_rule()


    # Rules for node AlpLiteral
    rule_AlpLiteral_0 = rule.Rule('AlpLiteral', rule.RuleEntry('LITERAL', key=None, ignore='-'), rule.RuleEntry('ID', key=None, ignore=None), rule.RuleEntry('STRING', key=None, ignore=None), rule.RuleEntry('AlpTokenMetainfoList', key=None, ignore=None))
    def p_AlpLiteral_0(self, p):
        p[0] = self.rule_AlpLiteral_0(AlpLiteral, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpLiteral_0.__doc__ = rule_AlpLiteral_0.to_yacc_rule()


    # Rules for node AlpKeyword
    rule_AlpKeyword_0 = rule.Rule('AlpKeyword', rule.RuleEntry('KEYWORD', key=None, ignore='-'), rule.RuleEntry('ID', key=None, ignore=None))
    def p_AlpKeyword_0(self, p):
        p[0] = self.rule_AlpKeyword_0(AlpKeyword, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpKeyword_0.__doc__ = rule_AlpKeyword_0.to_yacc_rule()


    # Rules for node AlpIgnore
    rule_AlpIgnore_0 = rule.Rule('AlpIgnore', rule.RuleEntry('IGNORE', key=None, ignore='-'), rule.RuleEntry('ID', key=None, ignore=None), rule.RuleEntry('STRING', key=None, ignore=None))
    def p_AlpIgnore_0(self, p):
        p[0] = self.rule_AlpIgnore_0(AlpIgnore, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpIgnore_0.__doc__ = rule_AlpIgnore_0.to_yacc_rule()


    # Rules for node SelParser
    rule_SelParser_0 = rule.Rule('SelParser', rule.RuleEntry('AlpPrecedence', key=None, ignore=None))
    def p_SelParser_0(self, p):
        p[0] = self.rule_SelParser_0(SelParser, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_SelParser_0.__doc__ = rule_SelParser_0.to_yacc_rule()

    rule_SelParser_1 = rule.Rule('SelParser', rule.RuleEntry('AlpNode', key=None, ignore=None))
    def p_SelParser_1(self, p):
        p[0] = self.rule_SelParser_1(SelParser, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_SelParser_1.__doc__ = rule_SelParser_1.to_yacc_rule()

    rule_SelParser_2 = rule.Rule('SelParser', rule.RuleEntry('AlpList', key=None, ignore=None))
    def p_SelParser_2(self, p):
        p[0] = self.rule_SelParser_2(SelParser, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_SelParser_2.__doc__ = rule_SelParser_2.to_yacc_rule()

    rule_SelParser_3 = rule.Rule('SelParser', rule.RuleEntry('AlpSelection', key=None, ignore=None))
    def p_SelParser_3(self, p):
        p[0] = self.rule_SelParser_3(SelParser, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_SelParser_3.__doc__ = rule_SelParser_3.to_yacc_rule()


    # Rules for node AlpPrecedence
    rule_AlpPrecedence_0 = rule.Rule('AlpPrecedence', rule.RuleEntry('PRECEDENCE', key=None, ignore='-'), rule.RuleEntry('LEFT', key=None, ignore=None), rule.RuleEntry('LPAREN', key=None, ignore='-'), rule.RuleEntry('AlpIdList', key=None, ignore=None), rule.RuleEntry('RPAREN', key=None, ignore='-'))
    def p_AlpPrecedence_0(self, p):
        p[0] = self.rule_AlpPrecedence_0(AlpPrecedence, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpPrecedence_0.__doc__ = rule_AlpPrecedence_0.to_yacc_rule()

    rule_AlpPrecedence_1 = rule.Rule('AlpPrecedence', rule.RuleEntry('PRECEDENCE', key=None, ignore='-'), rule.RuleEntry('RIGHT', key=None, ignore=None), rule.RuleEntry('LPAREN', key=None, ignore='-'), rule.RuleEntry('AlpIdList', key=None, ignore=None), rule.RuleEntry('RPAREN', key=None, ignore='-'))
    def p_AlpPrecedence_1(self, p):
        p[0] = self.rule_AlpPrecedence_1(AlpPrecedence, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpPrecedence_1.__doc__ = rule_AlpPrecedence_1.to_yacc_rule()


    # Rules for node AlpNode
    rule_AlpNode_0 = rule.Rule('AlpNode', rule.RuleEntry('NODE', key=None, ignore='-'), rule.RuleEntry('ID', key=None, ignore=None), rule.RuleEntry('LCURLY', key=None, ignore='-'), rule.RuleEntry('AlpNodeBody', key=None, ignore=None), rule.RuleEntry('RCURLY', key=None, ignore='-'))
    def p_AlpNode_0(self, p):
        p[0] = self.rule_AlpNode_0(AlpNode, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpNode_0.__doc__ = rule_AlpNode_0.to_yacc_rule()


    # Rules for node AlpList
    rule_AlpList_0 = rule.Rule('AlpList', rule.RuleEntry('LIST', key=None, ignore='-'), rule.RuleEntry('ID', key=None, ignore=None), rule.RuleEntry('LCURLY', key=None, ignore='-'), rule.RuleEntry('AlpRuleList', key=None, ignore=None), rule.RuleEntry('RCURLY', key=None, ignore='-'))
    def p_AlpList_0(self, p):
        p[0] = self.rule_AlpList_0(AlpList, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpList_0.__doc__ = rule_AlpList_0.to_yacc_rule()


    # Rules for node AlpSelection
    rule_AlpSelection_0 = rule.Rule('AlpSelection', rule.RuleEntry('SELECTION', key=None, ignore='-'), rule.RuleEntry('ID', key=None, ignore=None), rule.RuleEntry('LCURLY', key=None, ignore='-'), rule.RuleEntry('AlpRuleList', key=None, ignore=None), rule.RuleEntry('RCURLY', key=None, ignore='-'))
    def p_AlpSelection_0(self, p):
        p[0] = self.rule_AlpSelection_0(AlpSelection, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpSelection_0.__doc__ = rule_AlpSelection_0.to_yacc_rule()


    # Rules for node AlpNodeBody
    rule_AlpNodeBody_0 = rule.Rule('AlpNodeBody', rule.RuleEntry('AlpPropertyList', key=None, ignore=None), rule.RuleEntry('AlpRuleList', key=None, ignore=None))
    def p_AlpNodeBody_0(self, p):
        p[0] = self.rule_AlpNodeBody_0(AlpNodeBody, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpNodeBody_0.__doc__ = rule_AlpNodeBody_0.to_yacc_rule()


    # Rules for node AlpPropertyList
    rule_AlpPropertyList_0 = rule.Rule('AlpPropertyList')
    def p_AlpPropertyList_0(self, p):
        p[0] = self.rule_AlpPropertyList_0(AlpPropertyList, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpPropertyList_0.__doc__ = rule_AlpPropertyList_0.to_yacc_rule()

    rule_AlpPropertyList_1 = rule.Rule('AlpPropertyList', rule.RuleEntry('AlpProperty', key='head', ignore=None), rule.RuleEntry('SEMICOLON', key=None, ignore='-'), rule.RuleEntry('AlpPropertyList', key='body', ignore=None))
    def p_AlpPropertyList_1(self, p):
        p[0] = self.rule_AlpPropertyList_1(AlpPropertyList, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpPropertyList_1.__doc__ = rule_AlpPropertyList_1.to_yacc_rule()


    # Rules for node AlpProperty
    rule_AlpProperty_0 = rule.Rule('AlpProperty', rule.RuleEntry('REQUIRED', key=None, ignore=None), rule.RuleEntry('ID', key=None, ignore=None))
    def p_AlpProperty_0(self, p):
        p[0] = self.rule_AlpProperty_0(AlpProperty, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpProperty_0.__doc__ = rule_AlpProperty_0.to_yacc_rule()

    rule_AlpProperty_1 = rule.Rule('AlpProperty', rule.RuleEntry('OPTIONAL', key=None, ignore=None), rule.RuleEntry('ID', key=None, ignore=None))
    def p_AlpProperty_1(self, p):
        p[0] = self.rule_AlpProperty_1(AlpProperty, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpProperty_1.__doc__ = rule_AlpProperty_1.to_yacc_rule()


    # Rules for node AlpRuleList
    rule_AlpRuleList_0 = rule.Rule('AlpRuleList', rule.RuleEntry('AlpRule', key='head', ignore=None), rule.RuleEntry('SEMICOLON', key=None, ignore='-'))
    def p_AlpRuleList_0(self, p):
        p[0] = self.rule_AlpRuleList_0(AlpRuleList, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpRuleList_0.__doc__ = rule_AlpRuleList_0.to_yacc_rule()

    rule_AlpRuleList_1 = rule.Rule('AlpRuleList', rule.RuleEntry('AlpRule', key='head', ignore=None), rule.RuleEntry('SEMICOLON', key=None, ignore='-'), rule.RuleEntry('AlpRuleList', key='body', ignore=None))
    def p_AlpRuleList_1(self, p):
        p[0] = self.rule_AlpRuleList_1(AlpRuleList, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpRuleList_1.__doc__ = rule_AlpRuleList_1.to_yacc_rule()


    # Rules for node AlpRule
    rule_AlpRule_0 = rule.Rule('AlpRule', rule.RuleEntry('RULE', key=None, ignore='-'), rule.RuleEntry('AlpRuleEntryList', key=None, ignore=None), rule.RuleEntry('AlpRuleMetainfoList', key=None, ignore=None))
    def p_AlpRule_0(self, p):
        p[0] = self.rule_AlpRule_0(AlpRule, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpRule_0.__doc__ = rule_AlpRule_0.to_yacc_rule()


    # Rules for node AlpRuleEntryList
    rule_AlpRuleEntryList_0 = rule.Rule('AlpRuleEntryList')
    def p_AlpRuleEntryList_0(self, p):
        p[0] = self.rule_AlpRuleEntryList_0(AlpRuleEntryList, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpRuleEntryList_0.__doc__ = rule_AlpRuleEntryList_0.to_yacc_rule()

    rule_AlpRuleEntryList_1 = rule.Rule('AlpRuleEntryList', rule.RuleEntry('AlpRuleEntry', key='head', ignore=None), rule.RuleEntry('AlpRuleEntryList', key='body', ignore=None))
    def p_AlpRuleEntryList_1(self, p):
        p[0] = self.rule_AlpRuleEntryList_1(AlpRuleEntryList, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpRuleEntryList_1.__doc__ = rule_AlpRuleEntryList_1.to_yacc_rule()


    # Rules for node AlpRuleEntry
    rule_AlpRuleEntry_0 = rule.Rule('AlpRuleEntry', rule.RuleEntry('ID', key='name', ignore=None))
    def p_AlpRuleEntry_0(self, p):
        p[0] = self.rule_AlpRuleEntry_0(AlpRuleEntry, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpRuleEntry_0.__doc__ = rule_AlpRuleEntry_0.to_yacc_rule()

    rule_AlpRuleEntry_1 = rule.Rule('AlpRuleEntry', rule.RuleEntry('ID', key='key', ignore=None), rule.RuleEntry('EQ', key=None, ignore='-'), rule.RuleEntry('ID', key='name', ignore=None))
    def p_AlpRuleEntry_1(self, p):
        p[0] = self.rule_AlpRuleEntry_1(AlpRuleEntry, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpRuleEntry_1.__doc__ = rule_AlpRuleEntry_1.to_yacc_rule()

    rule_AlpRuleEntry_2 = rule.Rule('AlpRuleEntry', rule.RuleEntry('MINUS', key='ignored', ignore=None), rule.RuleEntry('ID', key='name', ignore=None))
    def p_AlpRuleEntry_2(self, p):
        p[0] = self.rule_AlpRuleEntry_2(AlpRuleEntry, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpRuleEntry_2.__doc__ = rule_AlpRuleEntry_2.to_yacc_rule()


    # Rules for node AlpModuleName
    rule_AlpModuleName_0 = rule.Rule('AlpModuleName', rule.RuleEntry('ID', key='head', ignore=None))
    def p_AlpModuleName_0(self, p):
        p[0] = self.rule_AlpModuleName_0(AlpModuleName, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpModuleName_0.__doc__ = rule_AlpModuleName_0.to_yacc_rule()

    rule_AlpModuleName_1 = rule.Rule('AlpModuleName', rule.RuleEntry('ID', key='head', ignore=None), rule.RuleEntry('PERIOD', key=None, ignore='-'), rule.RuleEntry('AlpModuleName', key='body', ignore=None))
    def p_AlpModuleName_1(self, p):
        p[0] = self.rule_AlpModuleName_1(AlpModuleName, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpModuleName_1.__doc__ = rule_AlpModuleName_1.to_yacc_rule()


    # Rules for node AlpIdList
    rule_AlpIdList_0 = rule.Rule('AlpIdList', rule.RuleEntry('ID', key='head', ignore=None))
    def p_AlpIdList_0(self, p):
        p[0] = self.rule_AlpIdList_0(AlpIdList, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpIdList_0.__doc__ = rule_AlpIdList_0.to_yacc_rule()

    rule_AlpIdList_1 = rule.Rule('AlpIdList', rule.RuleEntry('ID', key='head', ignore=None), rule.RuleEntry('COLON', key=None, ignore='-'), rule.RuleEntry('AlpIdList', key='body', ignore=None))
    def p_AlpIdList_1(self, p):
        p[0] = self.rule_AlpIdList_1(AlpIdList, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpIdList_1.__doc__ = rule_AlpIdList_1.to_yacc_rule()


    # Rules for node AlpRuleMetainfoList
    rule_AlpRuleMetainfoList_0 = rule.Rule('AlpRuleMetainfoList')
    def p_AlpRuleMetainfoList_0(self, p):
        p[0] = self.rule_AlpRuleMetainfoList_0(AlpRuleMetainfoList, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpRuleMetainfoList_0.__doc__ = rule_AlpRuleMetainfoList_0.to_yacc_rule()

    rule_AlpRuleMetainfoList_1 = rule.Rule('AlpRuleMetainfoList', rule.RuleEntry('AlpRuleMetainfo', key='head', ignore=None), rule.RuleEntry('AlpRuleMetainfoList', key='body', ignore=None))
    def p_AlpRuleMetainfoList_1(self, p):
        p[0] = self.rule_AlpRuleMetainfoList_1(AlpRuleMetainfoList, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpRuleMetainfoList_1.__doc__ = rule_AlpRuleMetainfoList_1.to_yacc_rule()


    # Rules for node AlpTokenMetainfoList
    rule_AlpTokenMetainfoList_0 = rule.Rule('AlpTokenMetainfoList')
    def p_AlpTokenMetainfoList_0(self, p):
        p[0] = self.rule_AlpTokenMetainfoList_0(AlpTokenMetainfoList, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpTokenMetainfoList_0.__doc__ = rule_AlpTokenMetainfoList_0.to_yacc_rule()

    rule_AlpTokenMetainfoList_1 = rule.Rule('AlpTokenMetainfoList', rule.RuleEntry('AlpTokenMetainfo', key='head', ignore=None), rule.RuleEntry('AlpTokenMetainfoList', key='body', ignore=None))
    def p_AlpTokenMetainfoList_1(self, p):
        p[0] = self.rule_AlpTokenMetainfoList_1(AlpTokenMetainfoList, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpTokenMetainfoList_1.__doc__ = rule_AlpTokenMetainfoList_1.to_yacc_rule()


    # Rules for node AlpRuleMetainfo
    rule_AlpRuleMetainfo_0 = rule.Rule('AlpRuleMetainfo', rule.RuleEntry('AlpPrecedenceMetainfo', key=None, ignore=None))
    def p_AlpRuleMetainfo_0(self, p):
        p[0] = self.rule_AlpRuleMetainfo_0(AlpRuleMetainfo, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpRuleMetainfo_0.__doc__ = rule_AlpRuleMetainfo_0.to_yacc_rule()

    rule_AlpRuleMetainfo_1 = rule.Rule('AlpRuleMetainfo', rule.RuleEntry('AlpErrorMetainfo', key=None, ignore=None))
    def p_AlpRuleMetainfo_1(self, p):
        p[0] = self.rule_AlpRuleMetainfo_1(AlpRuleMetainfo, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpRuleMetainfo_1.__doc__ = rule_AlpRuleMetainfo_1.to_yacc_rule()

    rule_AlpRuleMetainfo_2 = rule.Rule('AlpRuleMetainfo', rule.RuleEntry('AlpWarningMetainfo', key=None, ignore=None))
    def p_AlpRuleMetainfo_2(self, p):
        p[0] = self.rule_AlpRuleMetainfo_2(AlpRuleMetainfo, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpRuleMetainfo_2.__doc__ = rule_AlpRuleMetainfo_2.to_yacc_rule()


    # Rules for node AlpTokenMetainfo
    rule_AlpTokenMetainfo_0 = rule.Rule('AlpTokenMetainfo', rule.RuleEntry('AlpErrorMetainfo', key=None, ignore=None))
    def p_AlpTokenMetainfo_0(self, p):
        p[0] = self.rule_AlpTokenMetainfo_0(AlpTokenMetainfo, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpTokenMetainfo_0.__doc__ = rule_AlpTokenMetainfo_0.to_yacc_rule()

    rule_AlpTokenMetainfo_1 = rule.Rule('AlpTokenMetainfo', rule.RuleEntry('AlpWarningMetainfo', key=None, ignore=None))
    def p_AlpTokenMetainfo_1(self, p):
        p[0] = self.rule_AlpTokenMetainfo_1(AlpTokenMetainfo, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpTokenMetainfo_1.__doc__ = rule_AlpTokenMetainfo_1.to_yacc_rule()


    # Rules for node AlpPrecedenceMetainfo
    rule_AlpPrecedenceMetainfo_0 = rule.Rule('AlpPrecedenceMetainfo', rule.RuleEntry('PRECSYM', key=None, ignore='-'), rule.RuleEntry('ID', key=None, ignore=None))
    def p_AlpPrecedenceMetainfo_0(self, p):
        p[0] = self.rule_AlpPrecedenceMetainfo_0(AlpPrecedenceMetainfo, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpPrecedenceMetainfo_0.__doc__ = rule_AlpPrecedenceMetainfo_0.to_yacc_rule()


    # Rules for node AlpErrorMetainfo
    rule_AlpErrorMetainfo_0 = rule.Rule('AlpErrorMetainfo', rule.RuleEntry('ERRSYM', key=None, ignore='-'), rule.RuleEntry('STRING', key=None, ignore=None))
    def p_AlpErrorMetainfo_0(self, p):
        p[0] = self.rule_AlpErrorMetainfo_0(AlpErrorMetainfo, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpErrorMetainfo_0.__doc__ = rule_AlpErrorMetainfo_0.to_yacc_rule()


    # Rules for node AlpWarningMetainfo
    rule_AlpWarningMetainfo_0 = rule.Rule('AlpWarningMetainfo', rule.RuleEntry('WARNSYM', key=None, ignore='-'), rule.RuleEntry('STRING', key=None, ignore=None))
    def p_AlpWarningMetainfo_0(self, p):
        p[0] = self.rule_AlpWarningMetainfo_0(AlpWarningMetainfo, p[1:])
        if isinstance(p[0], ast.AstNodeBase):
            p[0].ast_location = self.get_location(p)
    p_AlpWarningMetainfo_0.__doc__ = rule_AlpWarningMetainfo_0.to_yacc_rule()



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

class Source(SourceBase):
    def load(self, resource, resource_locator=None):
        '''Load some file source.'''

        if resource_locator is not None:
            resource = resource_locator.find(resource)

        return parse_file(resource)
