from cgextra.matcher import matcher, cls

from base import AstBase

ast = cls(AstBase)

def node(typename):
    @matcher
    def __matcher(source, context):
        return typename in map(lambda c: c.__name__, source.__class__.__mro__)

    return __matcher
