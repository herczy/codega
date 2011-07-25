'''Implements the generic visitor interface'''

class MixinVisitor:
    '''A mixin to use with classes that need to implement visitors based on classes'''

    def visit(self, node, *args, **kwargs):
        '''Call the appropriate visitor method.

        The algorythm uses the method resolution order (__mro__) in
        order to decide which visitor method to call.
        '''

        for cls in node.__class__.__mro__:
            method = getattr(self, 'visit_%s' % cls.__name__, None)

            if method is not None:
                return method(node, *args, **kwargs)

        return self.visit_fallback(node, *args, **kwargs)

    def visit_fallback(self, node, *args, **kwargs):
        '''Fallback visitor, does nothing'''

class Visitor(object, MixinVisitor):
    '''Same as MixinVisitor extept that it's also a proper object-derived class'''
