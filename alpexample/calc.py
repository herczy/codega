import os.path
import sys
import operator
import readline
import atexit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from codega.logger import prepare
prepare()

import calcparser

from codega.alp.script import ParserError
from codega.visitor import ClassVisitor, visitor

class PrettyPrint(ClassVisitor):
    @visitor(calcparser.binary_expression)
    def v_binary_expr(self, o):
        return '(%s %s %s)' % (self.visit(o.properties.operand0), o.properties.operator, self.visit(o.properties.operand1))

    @visitor(calcparser.unary_expression)
    def v_unary_expr(self, o):
        return '(%s %s)' % (o.properties.operator, self.visit(o.properties.operand))

    @visitor(calcparser.assignment)
    def v_assign(self, o):
        return '%s = %s' % (o.properties.rvalue, self.visit(o.properties.lvalue))

    @visitor(calcparser.expr_for)
    def v_for(self, o):
        if o.properties.step is None:
            step = 1.0

        else:
            step = self.visit(o.properties.step)

        return '(for %s in %s to %s step %s do %s)' % (o.properties.bound, self.visit(o.properties.begin), self.visit(o.properties.end), step, self.visit(o.properties.assignment))

    def visit_fallback(self, o):
        return str(o)

vals = {}
class Evaluate(ClassVisitor):
    @visitor(calcparser.binary_expression)
    def v_binary_expr(self, o):
        operators = {'+' : operator.add, '-' : operator.sub, '*' : operator.mul, '/' : operator.div}
        return operators[o.properties.operator](self.visit(o.properties.operand0), self.visit(o.properties.operand1))

    @visitor(calcparser.unary_expression)
    def v_unary_expr(self, o):
        operators = {'-' : operator.neg}
        return operators[o.properties.operator](self.visit(o.properties.operand))

    @visitor(calcparser.assignment)
    def v_assign(self, o):
        vals[o.properties.rvalue] = self.visit(o.properties.lvalue)
        return vals[o.properties.rvalue]

    @visitor(calcparser.expr_for)
    def v_for(self, o):
        if o.properties.step is None:
            step = 1.0

        else:
            step = self.visit(o.properties.step)

        current = self.visit(o.properties.begin)
        end = self.visit(o.properties.end)

        res = 0.0
        while current < end:
            vals[o.properties.bound] = current
            res = self.visit(o.properties.assignment)

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
        ast = calcparser.parse(str(index), l)

    except calcparser.ParserError, e:
        print 'ERROR: %s' % e
        index += 1
        continue

    print '  [%d] %s => %.3lf' % (index, PrettyPrint().visit(ast), Evaluate().visit(ast))
    print

    index += 1
