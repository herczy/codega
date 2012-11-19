import os.path

from codega.generator.declarative import * #@UnusedWildImports
from codega.generator.priority import PRI_FALLBACK, PRI_HIGH
from codega.makowrapper import MakoTemplatesetFile

from codega.alp import script

from codega import matcher
from codega.variant import use_variant, variant

token_types = ('AlpToken', 'AlpLiteral', 'AlpIgnore', 'AlpKeyword')
parser_types = ('AlpNode', 'AlpSelection', 'AlpList')

def name_matcher(names):
    @matcher
    def __matcher(source, context):
        return source.name in names

    return __matcher

basepath = os.path.dirname(__file__)
template_path = os.path.join(basepath, 'scriptgen.mako')
ScriptMeta = create_declarative_metaclass()
templates = MakoTemplatesetFile(filename=template_path)

class ScriptBaseGenerator(Generator):
    __metaclass__ = ScriptMeta
    __base__ = True

    def generate(self, source, context):
        return templates.render(self.template, self.get_bindings(source, context))

class AlpScriptGenerator(ScriptBaseGenerator):
    __matcher__ = matcher.cls(script.AlpScript)

    template = 'AlpScript'

    def get_bindings(self, source, context):
        result = {}

        # Collect header information
        result.update(dict((h.key, h.value) for h in source.head))

        # Collect and render various information
        lexer = []
        parser = []
        ast = []
        precedence = []
        imports = []
        start = None
        for entry in source.body:
            if entry.ast_name in token_types:
                lexer.append(self.parent(entry, context))

            elif entry.ast_name in parser_types:
                parser.append(self.parent(entry, context))
                with use_variant(context, 'ast'):
                    ast.append(self.parent(entry, context))

            elif entry.ast_name == 'AlpPrecedence':
                precedence.append(self.parent(entry, context))

            elif entry.ast_name == 'AlpStart':
                start = entry.symbol

            elif entry.ast_name == 'AlpImport':
                imports.append(self.parent(entry, context))

        assert start is not None

        result.update(imports=imports, lexer=lexer, parser=parser, precedence=precedence, start=start, ast=ast)
        result.update(ctx=context)
        return result

class AlpImportGenerator(ScriptBaseGenerator):
    __matcher__ = matcher.cls(script.AlpImport)

    template = 'AlpImport'

    def get_bindings(self, source, context):
        return dict(source.ast_properties)

class TokenGeneratorBase(ScriptBaseGenerator):
    __base__ = True

    def get_attributes(self, source):
        return source.name, source.value[1:-1]

    def get_bindings(self, source, context):
        key, name = self.get_attributes(source)
        return dict(key=key, name=name)

class TokenGenerator(TokenGeneratorBase):
    __matcher__ = matcher.cls(script.AlpToken)
    template = 'AlpToken'

class LiteralGenerator(TokenGeneratorBase):
    __matcher__ = matcher.cls(script.AlpLiteral)
    template = 'AlpLiteral'

class IgnoreGenerator(TokenGeneratorBase):
    __matcher__ = matcher.cls(script.AlpIgnore)
    template = 'AlpIgnore'

class KeywordGenerator(ScriptBaseGenerator):
    __matcher__ = matcher.cls(script.AlpKeyword)
    template = 'AlpKeyword'

    def get_bindings(self, source, context):
        return dict(key=source.value)

class AstNodeGenerator(ScriptBaseGenerator):
    __priority__ = PRI_HIGH
    __matcher__ = matcher.all(variant('ast'), matcher.cls(script.AlpNode))
    template = 'AlpNode_ast'

    def get_bindings(self, source, context):
        body = source.body
        return dict(name=source.name, properties=context.map(self.parent, body.properties))

class AstListGenerator(ScriptBaseGenerator):
    __priority__ = PRI_HIGH
    __matcher__ = matcher.all(variant('ast'), matcher.cls(script.AlpList))
    template = 'AlpList_ast'

    def get_bindings(self, source, context):
        return dict(name=source.name)

class AstSelectionGenerator(ScriptBaseGenerator):
    __priority__ = PRI_HIGH
    __matcher__ = matcher.all(variant('ast'), matcher.cls(script.AlpSelection))
    template = 'AlpSelection_ast'

    def get_bindings(self, source, context):
        return dict(name=source.name)

class AstPropertyGenerator(ScriptBaseGenerator):
    __priority__ = PRI_HIGH
    __matcher__ = matcher.all(variant('ast'), matcher.cls(script.AlpProperty))
    template = 'AlpProperty_ast'

    def get_bindings(self, source, context):
        return dict(klass=source.klass.upper(), name=source.name)

class PrecedenceGenerator(ScriptBaseGenerator):
    __matcher__ = matcher.cls(script.AlpPrecedence)
    template = 'AlpPrecedence'

    def get_bindings(self, source, context):
        return dict(dir=source.direction, items=source.tokens)

class NodeGeneratorBase(ScriptBaseGenerator):
    __base__ = True

    def get_rules(self, name, context, rulelist):
        rules = []
        context.name = name
        try:
            for index, rule in enumerate(rulelist):
                context.index = index
                try:
                    rules.append(self.parent(rule, context))

                except:
                    raise

                finally:
                    del context.index

        finally:
            del context.name

        return rules

class NodeGenerator(NodeGeneratorBase):
    __matcher__ = matcher.cls(script.AlpNode)
    template = 'AlpNode'

    def get_bindings(self, source, context):
        body = source.body
        name = source.name

        return dict(name=name, rules=self.get_rules(name, context, body.rules))

class SelectionGenerator(NodeGeneratorBase):
    __matcher__ = matcher.any(matcher.cls(script.AlpSelection), matcher.cls(script.AlpList))
    template = 'AlpNode'

    def get_bindings(self, source, context):
        name = source.name

        return dict(name=name, rules=self.get_rules(name, context, source.body))

class RuleGenerator(ScriptBaseGenerator):
    __matcher__ = matcher.cls(script.AlpRule)
    template = 'AlpRule'

    def get_bindings(self, source, context):
        return dict(index=context.index, name=context.name, entries=context.map(self.parent, source.entries), precsym=source.precsymbol)

class RuleEntryGenerator(ScriptBaseGenerator):
    __matcher__ = matcher.cls(script.AlpRuleEntry)
    template = 'AlpRuleEntry'

    def get_bindings(self, source, context):
        return dict(source.ast_properties)

class FallbackGenerator(ScriptBaseGenerator):
    __priority__ = PRI_FALLBACK

    template = 'fallback'

    def get_bindings(self, source, context):
        return dict(a_source=source, a_context=context)

main_generator = MainGenerator(ScriptMeta)
