from codega.visitor import ClassVisitor, visitor
from codega.alp import script

class ValidationError(Exception):
    '''Validator-related error'''

class MissingSymbolError(ValidationError):
    '''Symbol missing'''

class DoubleDefinitionError(ValidationError):
    '''A symbol, script, etc. has been defined multiple times'''

class RuleError(ValidationError):
    '''An error has been detected in a rule'''

class Validator(ClassVisitor):
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

    @visitor(script.AlpScript)
    def visit_alp_script(self, ast):
        self.visit(ast.properties.head)
        self.visit(ast.properties.body)

    @visitor(script.AlpHeaderEntry)
    def visit_alp_header_entry(self, ast):
        if ast.properties.key in self._info:
            raise DoubleDefinitionError("Header information %r has been defined twice" % ast.key)

        self._info.add(ast.properties.key)

    @visitor(script.AlpStart)
    def visit_alp_start(self, ast):
        if self._start_symbol is not None:
            raise DoubleDefinitionError("The start symbol has been defined twice")

        self._start_symbol = ast.properties.symbol
        self._referenced_symbols.add(ast.properties.symbol)

    @visitor(script.AlpToken, script.AlpLiteral, script.AlpIgnore)
    def visit_alp_named_token(self, ast):
        self.check_duplicate_symbol(ast.properties.name)
        self._symbols.add(ast.properties.name)

    @visitor(script.AlpKeyword)
    def visit_alp_unnamed_token(self, ast):
        name = ast.properties.value.upper()
        self.check_duplicate_symbol(name)
        self._symbols.add(name)

    @visitor(script.AlpPrecedence)
    def visit_alp_precedence(self, ast):
        for entry in ast.properties.tokens:
            if entry in self._referenced_symbols:
                raise DoubleDefinitionError("Precedence symbol %r defined twice" % entry)

            self._referenced_symbols.add(entry)

    @visitor(script.AlpNode, script.AlpSelection)
    def visit_alp_node(self, ast):
        self.check_duplicate_symbol(ast.properties.name)
        self._symbols.add(ast.properties.name)

        self.visit(ast.properties.body)

    @visitor(script.AlpList)
    def visit_alp_list(self, ast):
        self.check_duplicate_symbol(ast.properties.name)
        self._symbols.add(ast.properties.name)
        self.visit(ast.properties.body)

        allowed_symbols = set(('tail', 'head', 'body'))

        for rule in ast.properties.body:
            for entry in rule.properties.entries:
                if entry.properties.ignored:
                    continue

                if entry.properties.key is None:
                    raise RuleError("List rule entry has no key")

                if entry.properties.key not in allowed_symbols:
                    raise RuleError("Invalid rule entry key %r found in a list node" % entry.properties.key)

    @visitor(script.AlpNodeBody)
    def visit_alp_node_body(self, ast):
        for _, value in ast.properties.items():
            self.visit(value)

    @visitor(script.AlpRule)
    def visit_alp_rule(self, ast):
        self.visit(ast.properties.entries)
        if ast.properties.precsymbol is not None:
            self._symbols.add(ast.properties.precsymbol)

        keys = set()
        for entry in ast.properties.entries:
            key = entry.properties.key
            if key is not None:
                if key in keys:
                    raise RuleError("Rule entry key %r defined twice" % key)

            keys.add(key)

    @visitor(script.AlpRuleEntry)
    def visit_alp_rule_entry(self, ast):
        self._referenced_symbols.add(ast.properties.name)

    @visitor(tuple)
    def visit_list(self, ast):
        for entry in ast:
            self.visit(entry)

    def visit_fallback(self, ast):
        pass
