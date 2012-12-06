from codega.visitor import ClassVisitor, visitor
from codega.alp import script
from codega.alp.ast import is_reserved, AstList


class ValidationError(Exception):
    '''Validator-related error'''


class MissingSymbolError(ValidationError):
    '''Symbol missing'''


class DoubleDefinitionError(ValidationError):
    '''A symbol, script, etc. has been defined multiple times'''


class RuleError(ValidationError):
    '''An error has been detected in a rule'''


class PropertyError(ValidationError):
    '''A property definition is invalid.'''


class MetainfoError(ValidationError):
    '''A metainfo is duplicated, invalid, etc.'''


class Validator(ClassVisitor):
    '''Validate the AST of an ALP language descriptor file.

    For validation instead of constructing an object and using visit,
    use the Validator.run class method.'''

    def __init__(self):
        super(Validator, self).__init__()

        # The starting symbol
        self._start_symbol = None

        # Symbols and information keys
        self._symbols = set()
        self._info = set()

        # Precedence directives
        self._precedence = set()

        # Symbols referenced in rules (must be checked)
        self._referenced_symbols = set()

    @classmethod
    def run(cls, ast):
        self = cls()
        self.visit(ast)

        # Check if there is a starting symbol
        if self._start_symbol is None:
            raise ValidationError("Starting symbol was not defined")

        # Check referenced symbols
        for sym in self._referenced_symbols:
            if sym not in self._symbols:
                raise MissingSymbolError("Symbol %r missing" % sym)

    def check_duplicate_symbol(self, name):
        if name in self._symbols:
            raise DoubleDefinitionError("Symbol %r has been defined twice" % name)

    def check_metainfo(self, ast):
        visited = set()
        dup = set()
        for key, _ in self.visit(ast.metainfo):
            if key in visited:
                dup.add(key)
            visited.add(key)

        if dup:
            strlist = ', '.join(repr(k) for k in dup)
            raise MetainfoError("The following metainfos are duplicated in %r: %s" % (ast, strlist))

        if 'error' in visited and 'warning' in visited:
            raise MetainfoError("Both warning and error set for %r" % ast)

    def get_metainfo_dict(self, ast):
        self.check_metainfo(ast)
        return dict(self.visit(ast.metainfo))

    @visitor(script.AlpScript)
    def visit_alp_script(self, ast):
        self.visit(ast.head)
        self.visit(ast.body)

    @visitor(script.AlpHeaderEntry)
    def visit_alp_header_entry(self, ast):
        if ast.key in self._info:
            raise DoubleDefinitionError("Header information %r has been defined twice" % ast.key)

        self._info.add(ast.key)

    @visitor(script.AlpStart)
    def visit_alp_start(self, ast):
        if self._start_symbol is not None:
            raise DoubleDefinitionError("The start symbol has been defined twice")

        self._start_symbol = ast.symbol
        self._referenced_symbols.add(ast.symbol)

    @visitor(script.AlpToken, script.AlpLiteral, script.AlpIgnore)
    def visit_alp_named_token(self, ast):
        if ast.ast_name != 'AlpIgnore':
            self.check_metainfo(ast)

        self.check_duplicate_symbol(ast.name)
        self._symbols.add(ast.name)

    @visitor(script.AlpKeyword)
    def visit_alp_unnamed_token(self, ast):
        name = ast.value.upper()
        self.check_duplicate_symbol(name)
        self._symbols.add(name)

    @visitor(script.AlpPrecedence)
    def visit_alp_precedence(self, ast):
        for entry in ast.tokens:
            if entry in self._referenced_symbols:
                raise DoubleDefinitionError("Precedence symbol %r defined twice" % entry)

            self._referenced_symbols.add(entry)

    @visitor(script.AlpNode)
    def visit_alp_node(self, ast):
        self.check_duplicate_symbol(ast.name)
        self._symbols.add(ast.name)

        self.visit(ast.body)

        members = set()
        for property in ast.body.properties:
            if is_reserved(property.name):
                raise PropertyError("%s is reserved as a property" % property.name)

            members.add(property.name)

        for rule in ast.body.rules:
            for entry in rule.entries:
                if entry.ignored:
                    continue

                if entry.key is not None and entry.key not in members:
                    raise RuleError("Node rule entry key %r not in property list" % entry.key)

    @visitor(script.AlpSelection)
    def visit_alp_selection(self, ast):
        self.check_duplicate_symbol(ast.name)
        self._symbols.add(ast.name)

        self.visit(ast.body)

        for rule in ast.body:
            count = 0
            for entry in rule.entries:
                if entry.ignored:
                    continue

                if entry.key is not None:
                    raise RuleError("Selection rule entry can not have a key")

                count += 1

            if count == 0:
                raise RuleError("Selection rule has no non-ignored entry")

            if count > 1:
                raise RuleError("Selection rule has too many non-ignored entries")

    @visitor(script.AlpList)
    def visit_alp_list(self, ast):
        self.check_duplicate_symbol(ast.name)
        self._symbols.add(ast.name)
        self.visit(ast.body)

        allowed_symbols = set(('tail', 'head', 'body'))

        for rule in ast.body:
            for entry in rule.entries:
                if entry.ignored:
                    continue

                if entry.key is None:
                    raise RuleError("List rule entry has no key")

                if entry.key not in allowed_symbols:
                    raise RuleError("Invalid rule entry key %r found in a list node" % entry.key)

    @visitor(script.AlpNodeBody)
    def visit_alp_node_body(self, ast):
        for _, value in ast.ast_properties.items():
            self.visit(value)

    @visitor(script.AlpRule)
    def visit_alp_rule(self, ast):
        self.visit(ast.entries)

        metainfo = self.get_metainfo_dict(ast)

        if 'prec' in metainfo:
            self._symbols.add(metainfo['prec'].prec)

        keys = set()
        for entry in ast.entries:
            key = entry.key
            if key is not None:
                if key in keys:
                    raise RuleError("Rule entry key %r defined twice" % key)

            keys.add(key)

    @visitor(script.AlpRuleEntry)
    def visit_alp_rule_entry(self, ast):
        self._referenced_symbols.add(ast.name)

    @visitor(script.AlpErrorMetainfo)
    def visit_alp_metainfo_error(self, ast):
        return 'error', ast

    @visitor(script.AlpWarningMetainfo)
    def visit_alp_metainfo_warning(self, ast):
        return 'warning', ast

    @visitor(script.AlpPrecedenceMetainfo)
    def visit_alp_metainfo_precsym(self, ast):
        return 'prec', ast

    @visitor(AstList)
    def visit_list(self, ast):
        res = []
        for entry in ast:
            res.append(self.visit(entry))

        return tuple(res)

    def visit_fallback(self, ast):
        pass
