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
from lxml import etree

import heapq
import types

from error import StateError
from decorators import abstract
import logger

PRI_HIGHEST = -100
PRI_HIGH = -10
PRI_BASE = 0
PRI_LOW  = 10
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

    def __init__(self, config = None, matcher = None, priority = PRI_BASE):
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

    def match(self, source):
        '''Check if the source node matches some criteria.

        Arguments:
        source -- Source node
        '''

        if self._matcher is None:
            return True

        return self._matcher(source)

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
        if not self.match(source):
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

class PriorityGenerator(GeneratorBase):
    '''A list of generators which are tried one-by-one until one can handle the source

    Members:
    _generators -- Heap-sorted list of generators. Items are in (priority, generator) format
    '''

    _generators = None

    def __internal_matcher(self, source):
        '''Matching is done by aggregating the matchers of registered sub-generators'''

        for pri, gen in self._generators:
            if gen.match(source):
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

        heapq.heappush(self._generators, (generator.priority, generator))
        generator.bind(self)

    def generate(self, source, context):
        '''Try to generate source with each contained generator instance'''

        heap = list(self._generators)

        while heap:
            pri, gen = heapq.heappop(heap)

            if gen.match(source):
                logger.debug('Generating source %r with priority generator %r (matching sub-generator %r)' % (source, self, gen))
                return gen.generate(source, context)

        raise ValueError("Source cannot be generated")

#
# Object generators
#
class ObjectGenerator(PriorityGenerator):
    '''The list of generators is extracted from the instance on start'''

    def __init__(self, priority = PRI_BASE):
        super(ObjectGenerator, self).__init__(priority = priority)

        self._collect()

    def _collect(self):
        '''Collect subgenerators from instance'''

        logger.info('Initializing object generator %r' % self)
        for attr in dir(self):
            val = getattr(self, attr)

            if isinstance(val, GeneratorBase):
                self.register(val)
                logger.debug('Registered subgenerator %r' % val)
