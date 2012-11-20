<%!

    from codega.indent import indent as _indent, disclaimer

    def indent(source, level=1):
        return _indent(source, level=level, indent_string='    ')

    def unescape(string):
        return ''.join(s for s in string[1:-1] if s != '\\')

    def process_token_metainfo(prefix, source):
        res = list(prefix)
        for meta in source.metainfo:
            if meta.ast_name == 'AlpErrorMetainfo':
                res.append('error=%r' % unescape(meta.message_format))

            elif meta.ast_name == 'AlpWarningMetainfo':
                res.append('warning=%r' % unescape(meta.message_format))

        return res

%>

<%def name='AlpScript()'>\
% if ctx.config is not None:
${disclaimer(ctx)}
% endif

__version__ = '${version or "Unknown"}'
__language__ = '${language or "Unknown"}'

__author__ = ${author or "'Unknown'"}
__email__ = ${email or "'Unknown'"}

from codega.alp.lexer import LexerFactory
from codega.alp.parser import ParserBase
from codega.alp.errorcontext import ErrorContext
from codega.alp import tools
from codega.alp import rule
from codega.alp import ast

% for imp in imports:
${imp}
% endfor

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
metainfo = ast.Metainfo()

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

<%def name='AlpImport()'>\
<%

    asexpr = ''
    if import_as is not None:
        asexpr = ' as %s' % import_as
        
    if import_from is None:
        _import_name = '.'.join(import_name)
    else:
        _import_name = import_name

%>\
% if import_from is not None:
from ${'.'.join(import_from)} \
% endif
import ${_import_name}${asexpr}\
</%def>

<%def name='AlpToken()'>\
lexer_factory.add_token(${', '.join(process_token_metainfo(("'" + key + "'", "'" + name + "'"), source))})\
</%def>

<%def name='AlpLiteral()'>\
lexer_factory.add_literal(${', '.join(process_token_metainfo(("'" + key + "'", "'" + name + "'"), source))})\
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
${name}_properties = (
% for prop in properties:
${indent(prop, level=1)},
% endfor
)
${name}_info = ast.Info('${name}', ${name}_properties)
${name} = ${name}_info.get_class(metainfo)
</%def>

<%def name='AlpList_ast()'>\
def ${name}(**kwargs):
    body = kwargs.pop('body', ())

    if 'head' in kwargs:
        head = kwargs.pop('head')
        body = (head,) + body

    if 'tail' in kwargs:
        tail = kwargs.pop('tail')
        body = body + (tail,)

    return body
</%def>

<%def name='AlpSelection_ast()'>\
# Helper class for selectors!
def ${name}(arg):
    return arg
</%def>

<%def name='AlpProperty_ast()'>('${name}', ast.${klass})</%def>

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

    metainfo = dict((meta.ast_name, meta) for meta in source.metainfo)
    rulename = 'rule_%s_%s' % (name, index)

    skip_apply = 'AlpErrorMetainfo' in metainfo

%>\
${rulename} = rule.Rule(${', '.join(args)})
% if 'AlpPrecedenceMetainfo' in metainfo:
${rulename}.precedence = '${metainfo['AlpPrecedenceMetainfo'].prec}'
% endif
def p_${name}_${index}(self, p):
% if 'AlpErrorMetainfo' in metainfo:
    self.report_error(${metainfo['AlpErrorMetainfo'].message_format}, self.${rulename}, p)
% endif
% if 'AlpWarningMetainfo' in metainfo:
    self.report_warning(${metainfo['AlpWarningMetainfo'].message_format}, self.${rulename}, p)
% endif
% if not skip_apply:
    p[0] = self.${rulename}(${name}, p[1:])
    if isinstance(p[0], ast.AstNodeBase):
        p[0].ast_location = self.get_location(p)
% endif
p_${name}_${index}.__doc__ = rule_${name}_${index}.to_yacc_rule()
</%def>

<%def name='AlpRuleEntry()'>\
rule.RuleEntry('${name}', key=${repr(key)}, ignore=${repr(ignored)})\
</%def>

<%def name='fallback()'>\
# Unknown item ${a_source.name}\
</%def>
