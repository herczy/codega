'''Generator handling

This module is responsible for defining different generator classes. While the GeneratorBase
only supplies the API, further generators have extended functionality.

Special constants:
PRI_HIGHEST -- Highest priority
PRI_HIGH -- High priority
PRI_BASE -- Base priority
PRI_LOW -- Low priority
PRI_LOWEST -- Lowest priority
PRI_FALLBACK -- Fallback priority
'''

import heapq
import types

from error import StateError
from decorators import *
import logger

PRI_HIGHEST = -100
PRI_HIGH = -10
PRI_BASE = 0
PRI_LOW = 10
PRI_LOWEST = 100
PRI_FALLBACK = 1000

class GeneratorBase(object):
    '''Generator base class'''

    def validate(self, source, context):
        '''Validate source

        Arguments:
        source -- Source node
        context -- Validation context
        '''

    @abstract
    def generate(self, source, context):
        '''Generate output and return it

        Arguments:
        source -- Source XML tree
        context -- Generation context
        '''

    def __call__(self, source, context):
        self.validate(source, context)
        return self.generate(source, context)

    def __str__(self):
        return 'generator:%d' % id(self)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self)

    @classmethod
    def run(cls, source, context):
        obj = cls()
        return obj(source, context)

class FunctionGenerator(GeneratorBase):
    '''A function is provided to do the generation

    Members:
    _function -- Generator function
    '''

    _function = None

    def __init__(self, generator):
        super(FunctionGenerator, self).__init__()

        self._function = generator

    def generate(self, source, context):
        return self._function(source, context)

    @classmethod
    def factory(cls, func):
        return cls(func)

class TemplateGenerator(GeneratorBase):
    '''Generates output with a template.

    Members:
    _template -- Template class
    _bindings -- Function generating bindings
    '''

    _template = None
    _bindings = None

    def __init__(self, template, bindings):
        super(TemplateGenerator, self).__init__()

        self._template = template
        self._bindings = bindings

    def generate(self, source, context):
        return self._template.render(self._bindings(source, context))

    @classmethod
    def factory(cls, template):
        '''Create a factory for template generator'''

        def __factory(func):
            return cls(template, func)

        return __factory

class FilterGenerator(FunctionGenerator):
    '''Filter the output of another generator. The priority and matchers are taken from
    the wrapped generator.
    
    Members:
    _filters -- The filter function(s)
    '''

    _filters = None

    def __init__(self, generator, *filters):
        super(FilterGenerator, self).__init__(generator)

        self._filters = list(filters)

    def generate(self, source, context):
        '''Generate an output from the subgenerator and call the filters on it'''

        output = super(FilterGenerator, self).generate(source, context)

        for filt in self._filters:
            output = filt(self, output)

        return output

    @classmethod
    def factory(cls, *filters):
        '''Decorate a generator function with a set of filters'''

        def __decorator(generator):
            return cls(generator, *filters)

        return __decorator

class PriorityGenerator(GeneratorBase):
    '''A list of generators which are tried one-by-one until one can handle the source

    Members:
    _generators -- Heap-sorted list of generators. Items are in (priority, generator) format
    '''

    _generators = None

    def __init__(self):
        super(PriorityGenerator, self).__init__()

        self._generators = []

    def register(self, generator, priority = PRI_BASE, matcher = None):
        '''Register a generator

        Arguments:
        generator -- Generator object
        priority -- Priority of generator
        matcher -- Generator matcher
        '''

        if not isinstance(generator, GeneratorBase):
            raise TypeError("Invalid generator type (not subclass of GeneratorBase)")

        heapq.heappush(self._generators, (priority, (generator, matcher)))

    def generate(self, source, context):
        '''Try to generate source with each contained generator instance'''

        heap = list(self._generators)

        while heap:
            pri, (gen, matcher) = heapq.heappop(heap)

            if matcher is None or matcher(source, context):
                logger.debug('Generating source %r with priority generator %r (matching sub-generator %r)' % (source, self, gen))
                return gen.generate(source, context)

        raise ValueError("Source cannot be generated")

#
# Object generators
#
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
