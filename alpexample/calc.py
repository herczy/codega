import os.path
import sys
import operator
import readline
import atexit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from codega.logger import prepare
prepare()

from codega.alp import enable_loader
enable_loader()

import calc as mod #@PydevCodeAnalysisIgnore

from codega.alp.script import ParserError
from codega.visitor import ClassVisitor, visitor

class PrettyPrint(ClassVisitor):
    @visitor(mod.binary_expression)
    def v_binary_expr(self, o):
        return '(%s %s %s)' % (self.visit(o.operand0), o.operator, self.visit(o.operand1))

    @visitor(mod.unary_expression)
    def v_unary_expr(self, o):
        return '(%s %s)' % (o.operator, self.visit(o.operand))

    @visitor(mod.assignment)
    def v_assign(self, o):
        return '%s = %s' % (o.rvalue, self.visit(o.lvalue))

    @visitor(mod.expr_for)
    def v_for(self, o):
        if o.step is None:
            step = 1.0

        else:
            step = self.visit(o.step)

        return '(for %s in %s to %s step %s do %s)' % (o.bound, self.visit(o.begin), self.visit(o.end), step, self.visit(o.assignment))

    def visit_fallback(self, o):
        return str(o)

vals = {}
class Evaluate(ClassVisitor):
    @visitor(mod.binary_expression)
    def v_binary_expr(self, o):
        operators = {'+' : operator.add, '-' : operator.sub, '*' : operator.mul, '/' : operator.div}
        return operators[o.operator](self.visit(o.operand0), self.visit(o.operand1))

    @visitor(mod.unary_expression)
    def v_unary_expr(self, o):
        operators = {'-' : operator.neg}
        return operators[o.operator](self.visit(o.operand))

    @visitor(mod.assignment)
    def v_assign(self, o):
        vals[o.rvalue] = self.visit(o.lvalue)
        return vals[o.rvalue]

    @visitor(mod.expr_for)
    def v_for(self, o):
        if o.step is None:
            step = 1.0

        else:
            step = self.visit(o.step)

        current = self.visit(o.begin)
        end = self.visit(o.end)

        res = 0.0
        while current < end:
            vals[o.bound] = current
            res = self.visit(o.assignment)

            current += step

        return res

    def visit_fallback(self, o):
        try:
            return float(o)

        except ValueError:
            try:
                return vals[o]

            except KeyError:
                return 0.0

histfile = os.path.join(os.path.dirname(__file__), ".history")
try:
    readline.read_history_file(histfile)
    index = open(histfile).read().count('\n')

except IOError:
    index = 0

atexit.register(readline.write_history_file, histfile)

while True:
    try:
        l = raw_input('[%d] ' % index)

    except:
        print
        print 'Bye'
        break

    try:
        ast = mod.parse(str(index), l)

    except ParserError, e:
        print 'ERROR: %s' % e
        index += 1
        continue

    print '  [%d] %s => %.3lf' % (index, PrettyPrint().visit(ast), Evaluate().visit(ast))
    print

    index += 1
