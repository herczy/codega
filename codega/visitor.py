'''Implements the generic visitor interface'''

import re

replacement = re.compile(r'[^A-Za-z0-9]')

def substitute(match):
    return '_%02x' % ord(match.group())

def chain_names(*names):
    return '_'.join(map(lambda name: replacement.sub(substitute, name), names))

def find_method(obj, prefix, *names):
    attributes = map(lambda name: chain_names(prefix, name), names)

    for attr in attributes:
        val = getattr(obj, attr, None)
        if val is not None:
            return val

class MixinVisitor:
    '''A mixin to use with classes that need to implement visitors based on classes'''

    def visit(self, node, *args, **kwargs):
        '''Call the appropriate visitor method.

        The algorithm uses the method resolution order (__mro__) in
        order to decide which visitor method to call.
        '''

        method = find_method(self, 'visit', *map(lambda cls: cls.__name__, node.__class__.__mro__))
        if method is not None:
            return method(node, *args, **kwargs)

        return self.visit_fallback(node, *args, **kwargs)

    def visit_fallback(self, node, *args, **kwargs):
        '''Fallback visitor, does nothing'''

class Visitor(object, MixinVisitor):
    '''Same as MixinVisitor extept that it's also a proper object-derived class'''
