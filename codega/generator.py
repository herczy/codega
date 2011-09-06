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
import copy

from error import StateError
from decorators import abstract
import logger

PRI_HIGHEST = -100
PRI_HIGH = -10
PRI_BASE = 0
PRI_LOW = 10
PRI_LOWEST = 100
PRI_FALLBACK = 1000

class GeneratorBase(object):
    '''Generator base class

    Arguments:
    _matcher -- Function that checks the source XML prior to generation
    _priority -- Priority of the generator
    _parent -- Parent of the generator or none for root generators
    '''

    _matcher = None
    _priority = None
    _parent = None

    def __init__(self, matcher = None, priority = PRI_BASE):
        self._matcher = matcher
        self._priority = priority

    @property
    def priority(self):
        '''Priority property'''

        return self._priority

    @property
    def parent(self):
        '''Parent property'''

        return self._parent

    def validate(self, source, context):
        '''Validate source

        Arguments:
        source -- Source node
        context -- Validation context
        '''

    def match(self, source, context):
        '''Check if the source node matches some criteria.

        Arguments:
        source -- Source node
        '''

        if self._matcher is None:
            return True

        return self._matcher(source, context)

    @abstract
    def generate(self, source, context):
        '''Generate output and return it

        Arguments:
        source -- Source XML tree
        context -- Generation context
        '''

    def bind(self, parent):
        '''Bind the generator to a parent.

        A generator can only be bound once, after that it's bound forever.

        Arguments:
        parent -- Parent generator
        '''

        if self._parent is not None:
            raise StateError("Generator already bound!")

        self._parent = parent

    def __call__(self, source, context):
        if not self.match(source, context):
            raise ValueError("Source cannot be generated because generator doesn't match the proper node")

        return self.generate(source, context)

    def __str__(self):
        return 'generator %d, priority = %d' % (id(self), self.priority)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self)

    @classmethod
    def run(cls, tree, context):
        generator = cls()
        generator.validate(tree, context)
        return generator.generate(tree, context)

class FunctionGenerator(GeneratorBase):
    '''A function is provided to do the generation

    Members:
    _function -- Generator function
    '''

    _function = None

    def __init__(self, generator, matcher = None, priority = PRI_BASE):
        super(FunctionGenerator, self).__init__(matcher = matcher, priority = priority)

        self._function = generator

    def generate(self, source, context):
        return self._function(source, context)

    def bind(self, parent):
        super(FunctionGenerator, self).bind(parent)

        self._function = types.MethodType(self._function, parent)

    def __str__(self):
        return 'function generator %s, priority = %d' % (self._function.__name__, self.priority)

    @staticmethod
    def decorate(matcher = None, priority = PRI_BASE):
        '''Creates a FunctionGenerator from the decorated function

        Arguments:
        matcher -- Generator matcher
        priority -- Generator function
        '''

        def __decorator(func):
            return FunctionGenerator(func, matcher = matcher, priority = priority)

        return __decorator

class TemplateGenerator(GeneratorBase):
    '''Generates output with a template.

    Members:
    _template -- Template class
    _bindings -- Function generating bindings
    '''

    _template = None
    _bindings = None

    def __init__(self, template, bindings, matcher = None, priority = PRI_BASE):
        super(TemplateGenerator, self).__init__(matcher = matcher, priority = priority)

        self._template = template
        self._bindings = bindings

    def generate(self, source, context):
        return self._template.render(self._bindings(source, context))

    def bind(self, parent):
        super(TemplateGenerator, self).bind(parent)

        self._bindings = types.MethodType(self._bindings, parent)

    def __str__(self):
        return 'template generator %s, priority = %d' % (self._bindings.__name__, self.priority)

    @staticmethod
    def decorate(template, matcher = None, priority = PRI_BASE):
        '''Creates a FunctionGenerator from the decorated function

        Arguments:
        template -- Template for the generator
        matcher -- Generator matcher
        priority -- Generator function
        '''

        def __decorator(func):
            return TemplateGenerator(template, func, matcher = matcher, priority = priority)

        return __decorator

class FilterGenerator(GeneratorBase):
    '''Filter the output of another generator. The priority and matchers are taken from
    the wrapped generator.
    
    Members:
    _subgenerator -- The wrapped generator
    _filters -- The filter function(s)
    '''

    _subgenerator = None
    _filters = None

    def __init__(self, generator, *filters):
        self._filters = filters
        self._subgenerator = generator

        super(FilterGenerator, self).__init__(matcher = generator.match, priority = generator.priority)

    def generate(self, source, context):
        '''Generate an output from the subgenerator and call the filters on it'''

        output = self._subgenerator(source, context)

        for filt in self._filters:
            output = filt(self, output)

        return output

    def bind(self, parent):
        super(FilterGenerator, self).bind(parent)
        self._subgenerator.bind(parent)

    def add_filter(self, filter):
        '''Appends a filter to the filter list'''

        self._filters.append(filter)

    @staticmethod
    def decorate(filter):
        '''Decorate a generator with a filter.
        
        Multiple filters are appended so a FilterGenerator isn't repeted'''

        def __decorator(generator):
            if isinstance(generator, FilterGenerator):
                generator.add_filter(filter)
                return generator

            return FilterGenerator(generator, filter)

        return __decorator

class PriorityGenerator(GeneratorBase):
    '''A list of generators which are tried one-by-one until one can handle the source

    Members:
    _generators -- Heap-sorted list of generators. Items are in (priority, generator) format
    '''

    _generators = None

    def __internal_matcher(self, source, context):
        '''Matching is done by aggregating the matchers of registered sub-generators'''

        for pri, gen in self._generators:
            if gen.match(source, context):
                return True

        return False

    def __init__(self, priority = PRI_BASE):
        super(PriorityGenerator, self).__init__(matcher = self.__internal_matcher, priority = priority)

        self._generators = []

    def register(self, generator):
        '''Register a generator

        Arguments:
        generator -- Generator object
        priority -- Priority of generator
        '''

        if not isinstance(generator, GeneratorBase):
            raise TypeError("Invalid generator type (not subclass of GeneratorBase)")

        generator_copy = copy.copy(generator)
        heapq.heappush(self._generators, (generator_copy.priority, generator_copy))
        generator_copy.bind(self)

    def generate(self, source, context):
        '''Try to generate source with each contained generator instance'''

        heap = list(self._generators)

        while heap:
            pri, gen = heapq.heappop(heap)

            if gen.match(source, context):
                logger.debug('Generating source %r with priority generator %r (matching sub-generator %r)' % (source, self, gen))
                return gen.generate(source, context)

        raise ValueError("Source cannot be generated")

#
# Object generators
#
class ObjectGenerator(PriorityGenerator):
    '''The list of generators is extracted from the instance on start'''

    __skip__ = ('_parent',)

    def __init__(self, priority = PRI_BASE):
        super(ObjectGenerator, self).__init__(priority = priority)

        self._collect()

    @classmethod
    def _collect_skip_list(cls):
        if not hasattr(cls, '_skip_resolved'):
            # Get collection of methods to skip
            skip_resolved = []

            for rescls in cls.__mro__:
                if issubclass(rescls, ObjectGenerator) and hasattr(rescls, '__skip__'):
                    skip_resolved.extend(rescls.__skip__)

            cls._skip_resolved = set(skip_resolved)

        return cls._skip_resolved

    def _collect(self):
        '''Collect subgenerators from instance'''

        # Check if object generator has a skip-set
        skip_set = self.__class__._collect_skip_list()

        logger.info('Initializing object generator %r' % self)
        for attr in dir(self):
            if attr in skip_set:
                logger.info('Skipping attribute %s since it\'s in the skip list' % attr)
                continue

            val = getattr(self, attr)

            if isinstance(val, GeneratorBase):
                self.register(val)
                logger.debug('Registered %s subgenerator %r' % (attr, val))
