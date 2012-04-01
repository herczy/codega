<%!

    from cgextra.indent import indent as _indent, disclaimer

    def indent(source, level=1):
        return _indent(source, level=level, indent_string='    ')

%>

<%def name='AlpScript()'>\
${disclaimer(ctx)}

__version__ = '${version or "Unknown"}'
__language__ = '${language or "Unknown"}'

__author__ = ${author or "'Unknown'"}
__email__ = ${email or "'Unknown'"}

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
% for lexentry in lexer:
${lexentry}
% endfor
Lexer = lexer_factory.create_class()

# AST nodes
AstBaseClass = ast.create_base_node('AstBaseClass')
% for node in ast:
${node}
% endfor

# Parser
class Parser(ParserBase):
    start = '${start}'

% if precedence:
    precedence = (
%   for prec in precedence:
${indent(prec, level=2)}
%   endfor 
    )
% endif
    
% for parsentry in parser: 
${indent(parsentry)}
% endfor

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
</%def>

<%def name='AlpToken()'>\
lexer_factory.add_token('${key}', '${name}');\
</%def>

<%def name='AlpLiteral()'>\
lexer_factory.add_literal('${key}', '${name}');\
</%def>

<%def name='AlpIgnore()'>\
lexer_factory.add_ignore_token('${key}', '${name}');\
</%def>

<%def name='AlpKeyword()'>\
lexer_factory.add_keyword('${key}');\
</%def>

<%def name='AlpPrecedence()'>\
<%

    args = (repr(dir),) + tuple(repr(i) for i in items)

%>\
(${', '.join(args)}),\
</%def>

<%def name='AlpNode_ast()'>\
class ${name}(AstBaseClass):
    property_definitions = (
% for prop in properties:
${indent(prop, level=2)},
% endfor
    )
</%def>

<%def name='AlpSelection_ast()'>\
# Helper class for selectors!
def ${name}(arg):
    return arg
</%def>

<%def name='AlpProperty_ast()'>\
ast.Property('${name}', klass=${klass})\
</%def>

<%def name='AlpNode()'>\
# Rules for node ${name}
% for rule in rules:
${rule}
% endfor
</%def>

<%def name='AlpRule()'>\
<%

    args = [ "'%s'" % name ]
    args.extend(entries)

%>\
rule_${name}_${index} = rule.Rule(${', '.join(args)})
% if precsym is not None:
rule_${name}_${index}.precedence = '${precsym}'
% endif
def p_${name}_${index}(self, p):
    p[0] = self.rule_${name}_${index}(${name}, p[1:])
p_${name}_${index}.__doc__ = rule_${name}_${index}.to_yacc_rule()
</%def>

<%def name='AlpRuleEntry()'>\
rule.RuleEntry('${entry.name}', key=${repr(entry.key)}, ignore=${repr(entry.ignored)})\
</%def>

<%def name='fallback()'>\
# Unknown item ${a_source.name}\
</%def>