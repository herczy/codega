'''
Flavors are a mechanism to mark the context temporarily. This is useful if the same
object generator needs to render the same kind of node with more than one sub-generator.
'''

from matcher import matcher

def flavor(flav):
    '''Matcher for checking the context for a flavor'''

    @matcher
    def __matcher(source, context):
        return getattr(context, 'flavor', None) == flav

    return __matcher

def seasoned(context, flavor):
    '''Set the flavor of the context. This call returns an object which has the
    enter/exit mechanism of Python (so the result should be used with `with`.
    
    The flavoring will be reversed on exit, so the context state is the same as
    it was prior to entering'''

    class __seasoning(object):
        def __enter__(self):
            self._exists = hasattr(context, 'flavor')
            self._original = getattr(context, 'flavor', None)

            context.flavor = flavor

        def __exit__(self, *args):
            if self._exists:
                context.flavor = self._original

            else:
                del context.flavor

    return __seasoning()

def get_flavor(context):
    '''Get the context flavor'''

    return getattr(context, 'flavor', None)
