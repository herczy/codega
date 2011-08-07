'''Implements the generic visitor interface'''

from decorators import abstract, mark, collect_marked

visitor = lambda value: mark('visit', value)

class VisitorType(type):
    '''Meta-class for visitor types.

    This meta-class collects the visitor methods into a dictionary to
    be used when doing a visitation.
    '''

    def __new__(cls, name, bases, mdict):
        mdict['__visitors__'] = dict(collect_marked(mdict, 'visit'))
        return type.__new__(cls, name, bases, mdict)

class VisitorBase(object):
    '''A base class for visitors'''

    __metaclass__ = VisitorType

    @abstract
    def aspects(self, node):
        '''Return the aspect of the node that will decide which
        visitor function to use'''

    def visit(self, node, *args, **kwargs):
        '''Call the appropriate visitor method.'''

        for aspect in self.aspects(node):
            if self.__visitors__.has_key(aspect):
                # We need to specify self in the call since these are not
                # bound methods
                return self.__visitors__[aspect](self, node, *args, **kwargs)

        return self.visit_fallback(node, *args, **kwargs)

    def visit_fallback(self, node, *args, **kwargs):
        '''Fallback visitor, does nothing'''

class ClassVisitor(VisitorBase):
    '''A visitor to use with classes that need to implement visitors based on classes'''

    def aspects(self, node):
        '''Use the method resolution order (__mro__) for identifying the visitor method to use.'''

        return node.__class__.__mro__

class XmlVisitor(VisitorBase):
    '''A visitor to use with XML nodes'''

    def aspects(self, node):
        '''Call the appropriate visitor method.'''

        return [ node.tag ]

class ExplicitVisitor(VisitorBase):
    '''A visitor where the only aspect is the node itself'''

    def aspects(self, node):
        return [ node ]
