'''
Variants are a mechanism to mark the context temporarily. This is useful if the same
object generator needs to render the same kind of node with more than one sub-generator.
This way, the sub-generator will be able to handle different variants of the same node
in different fashions.
'''

from matcher import matcher


def variant(var):
    '''Matcher for checking the context for a variant'''

    @matcher
    def __matcher(source, context):
        return getattr(context, 'variant', None) == var

    return __matcher


def use_variant(context, variant):
    '''
    Set the variant of the context. This call returns an object which has the
    enter/exit mechanism of Python (so the result should be used with `with`).

    The variant will be reversed on exit, so the context state is the same as
    it was prior to entering.
    '''

    class __variant_context(object):
        def __enter__(self):
            self._exists = hasattr(context, 'variant')
            self._original = getattr(context, 'variant', None)

            context.variant = variant

        def __exit__(self, *args):
            if self._exists:
                context.variant = self._original

            else:
                del context.variant

    return __variant_context()


def get_variant(context):
    '''Get the context variant'''

    return getattr(context, 'variant', None)
