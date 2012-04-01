from codega.visitor import ClassVisitor, visitor

from alplang import module

class ValidationError(Exception):
    '''Validator-related error'''

class MissingSymbolError(ValidationError):
    '''Symbol missing'''

class DoubleDefinitionError(ValidationError):
    '''A symbol, module, etc. has been defined multiple times'''

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
                print sym, self._symbols
                raise MissingSymbolError("Symbol %r missing" % sym)

    def check_duplicate_symbol(self, name):
        if name in self._symbols:
            raise DoubleDefinitionError("Symbol %r has been defined twice" % name)

    @visitor(module.AlpScript)
    def visit_alp_script(self, ast):
        self.visit(ast.properties.head)
        self.visit(ast.properties.body)

    @visitor(module.AlpHeaderEntry)
    def visit_alp_header_entry(self, ast):
        if ast.properties.key in self._info:
            raise DoubleDefinitionError("Header information %r has been defined twice" % ast.key)

        self._info.add(ast.properties.key)

    @visitor(module.AlpStart)
    def visit_alp_start(self, ast):
        if self._start_symbol is not None:
            raise DoubleDefinitionError("The start symbol has been defined twice")

        self._start_symbol = ast.properties.symbol
        self._referenced_symbols.add(ast.properties.symbol)

    @visitor(module.AlpToken, module.AlpLiteral, module.AlpIgnore)
    def visit_alp_named_token(self, ast):
        self.check_duplicate_symbol(ast.properties.name)
        self._symbols.add(ast.properties.name)

    @visitor(module.AlpKeyword)
    def visit_alp_unnamed_token(self, ast):
        name = ast.properties.value.upper()
        self.check_duplicate_symbol(name)
        self._symbols.add(name)

    @visitor(module.AlpPrecedence)
    def visit_alp_precedence(self, ast):
        for entry in ast.properties.list:
            if entry in self._referenced_symbols:
                raise DoubleDefinitionError("Precedence symbol %r defined twice" % entry)

            self._referenced_symbols.add(entry)

    @visitor(module.AlpNode, module.AlpSelection)
    def visit_alp_node(self, ast):
        self.check_duplicate_symbol(ast.properties.name)
        self._symbols.add(ast.properties.name)

        self.visit(ast.properties.body)

    @visitor(module.AlpNodeBody)
    def visit_alp_node_body(self, ast):
        for _, value in ast.properties.items():
            self.visit(value)

    @visitor(module.AlpRule)
    def visit_alp_rule(self, ast):
        self.visit(ast.properties.entries)

    @visitor(module.AlpRuleEntry)
    def visit_alp_rule_entry(self, ast):
        self._referenced_symbols.add(ast.properties.name)

    @visitor(tuple)
    def visit_list(self, ast):
        for entry in ast:
            self.visit(entry)

    def visit_fallback(self, ast):
        pass
