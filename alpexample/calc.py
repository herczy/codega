import os.path
import sys
import operator
import readline
import atexit
import math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from codega.visitor import ClassVisitor, visitor
from codega.logger import prepare
prepare()

import calcparser

class PrettyPrint(ClassVisitor):
    @visitor(calcparser.binary_expression)
    def v_binary_expr(self, o):
        return '(%s %s %s)' % (self.visit(o.operand0), o.operator, self.visit(o.operand1))

    @visitor(calcparser.unary_expression)
    def v_unary_expr(self, o):
        return '%s%s' % (o.operator, self.visit(o.operand))

    @visitor(calcparser.assignment)
    def v_assign(self, o):
        return '%s = %s' % (o.rvalue, self.visit(o.lvalue))

    @visitor(calcparser.call)
    def v_call(self, o):
        return '%s(%s)' % (o.func, ', '.join(self.visit(a) for a in o.args))

    @visitor(calcparser.expr_for)
    def v_for(self, o):
        if o.step is None:
            step = 1.0

        else:
            step = self.visit(o.step)

        return '(for %s in %s to %s step %s do %s)' % (o.bound, self.visit(o.begin), self.visit(o.end), step, self.visit(o.assignment))

    @visitor(calcparser.funcdef)
    def v_funcdef(self, o):
        return '%s(%s) = %s' % (o.name, ', '.join(self.visit(a) for a in o.args), self.visit(o.expression))

    def visit_fallback(self, o):
        return str(o)

vals = {}
funcs = {}
for a in dir(math):
    if a[0] == '_':
        continue

    v = getattr(math, a)
    if hasattr(v, '__call__'):
        funcs[a] = v

    else:
        vals[a] = v

class Evaluate(ClassVisitor):
    @visitor(calcparser.binary_expression)
    def v_binary_expr(self, o):
        operators = {'+' : operator.add, '-' : operator.sub, '*' : operator.mul, '/' : operator.div, '^' : operator.pow}
        return operators[o.operator](self.visit(o.operand0), self.visit(o.operand1))

    @visitor(calcparser.unary_expression)
    def v_unary_expr(self, o):
        operators = {'-' : operator.neg}
        return operators[o.operator](self.visit(o.operand))

    @visitor(calcparser.call)
    def v_call(self, o):
        return funcs[o.func](*(self.visit(a) for a in o.args))

    @visitor(calcparser.assignment)
    def v_assign(self, o):
        vals[o.rvalue] = self.visit(o.lvalue)
        return vals[o.rvalue]

    @visitor(calcparser.funcdef)
    def v_funcdef(self, o):
        def __func(*args):
            global vals
            oldvals = vals.copy()
            try:
                for arg_passed, arg_name in zip(args, o.args):
                    vals[arg_name] = arg_passed

                return self.visit(o.expression)

            finally:
                vals = oldvals

        global funcs
        funcs[o.name] = __func
        return 0.0

    @visitor(calcparser.expr_for)
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

    @visitor(calcparser.number)
    def v_num(self, o):
        return float(o.value)

    def visit_fallback(self, o):
        if isinstance(o, tuple):
            return (self.visit(e) for e in o)

        elif isinstance(o, basestring):
            try:
                return vals[o]

            except KeyError:
                return 0.0

        else:
            return o

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

    pp = '  [%d] %s => ' % (index, PrettyPrint().visit(ast))
    try:
        res = '%.3lf' % Evaluate().visit(ast)

    except Exception, e:
        res = 'ERROR: %s' % e

    print '%s%s' % (pp, res)
    print

    index += 1
