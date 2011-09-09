'''
Object generators collect specially marked methods and turn them into generators (depending on
the factory specified with generator).
'''

from codega.decorators import mark, has_mark, set_mark, get_mark, get_mark_default, collect_marked_bound
from codega import logger

from priority import PriorityGenerator, PRI_BASE

def generator(factory = None):
    '''Mark the function as a generator. If factory is set, the
    generator function will be passed to the factory and the result
    is used.'''

    return mark('generator', factory)

def match(matcher):
    '''Add a matcher to the generator'''

    def __decorate(func):
        if not has_mark(func, 'matchers'):
            set_mark(func, 'matchers', [])

        get_mark(func, 'matchers').append(matcher)
        return func

    return __decorate

def priority(priority):
    '''Specify priority of the generator'''

    return mark('priority', priority)

class ObjectGenerator(PriorityGenerator):
    '''The list of generators is extracted from the instance on start'''

    def __init__(self):
        super(ObjectGenerator, self).__init__()

        self._collect()

    @staticmethod
    def __get_internal_matcher(matchers):
        '''Create an internal matcher for registering a sub-generator in PriorityGenerator'''

        def __matcher(source, context):
            for matcher in matchers:
                if not matcher(source, context):
                    return False

            return True

        return __matcher

    def _collect(self):
        '''Collect subgenerators from instance'''

        for factory, generator in collect_marked_bound(self, 'generator'):
            priority = get_mark_default(generator, 'priority', PRI_BASE)
            matchers = get_mark_default(generator, 'matchers', [])

            logger.info('Registering sub-generator %r into generator %r; priority=%d, matchers=%r', generator, self, priority, matchers)

            if factory is not None:
                logger.debug('Factory found for sub-generator %r: %r', generator, factory)
                generator = factory(generator)

            self.register(generator, priority = priority, matcher = ObjectGenerator.__get_internal_matcher(matchers))
