'''Generator handling

This module is responsible for defining different generator classes. While the GeneratorBase
only supplies the API, further generators have extended functionality.
'''
from lxml import etree

import heapq
import types

class GeneratorBase(object):
    '''Generator base class

    Arguments:
    _matcher -- Function that checks the source XML prior to generation
    '''

    _matcher = None

    def __init__(self, matcher = None):
        self._matcher = matcher

    def match(self, source):
        '''Check if the source node matches some criteria.

        Arguments:
        source -- Source node
        '''

        if self._matcher is None:
            return True

        return self._matcher(source)

    def generate(self, source, target):
        '''Generate output and write it to target

        Arguments:
        source -- Source XML tree
        target -- Target file object (an object with write)
        '''

        raise NotImplementedError("GeneratorBase.generate is abstract")

    def __call__(self, source, target):
        if not self.match(source):
            raise ValueError("Source cannot be generated")

        self.generate(source, target)

class FunctionGenerator(GeneratorBase):
    '''A function is provided to do the generation

    Members:
    _function -- Generator function
    '''

    _function = None

    def __init__(self, generator, matcher = None):
        super(FunctionGenerator, self).__init__(matcher = matcher)

        self._function = generator

    def generate(self, source, target):
        self._function(source, target)

class TemplateGenerator(GeneratorBase):
    '''Generates output with a template.

    Members:
    _template -- Template class
    _bindings -- Function generating bindings
    '''

    _template = None
    _bindings = None

    def __init__(self, template, bindings, matcher = None):
        super(TemplateGenerator, self).__init__(matcher = matcher)

        self._template = template
        self._bindings = bindings

    def generate(self, source, target):
        target.write(self._template.render(self._bindings(source)))

class PriorityGenerator(GeneratorBase):
    '''A list of generators which are tried one-by-one until one can handle the source

    Members:
    _generators -- Heap-sorted list of generators. Items are in (priority, generator) format

    Static members:
    PRI_HIGHEST -- Highest priority
    PRI_HIGH -- High priority
    PRI_BASE -- Base priority
    PRI_LOW -- Low priority
    PRI_LOWEST -- Lowest priority
    PRI_FALLBACK -- Fallback priority
    '''

    PRI_HIGHEST = -100
    PRI_HIGH = -10
    PRI_BASE = 0
    PRI_LOW  = 10
    PRI_LOWEST = 100
    PRI_FALLBACK = 1000

    _generators = None

    def __init__(self, matcher = None):
        super(PriorityGenerator, self).__init__(matcher = matcher)

        self._generators = []

    def register(self, generator, priority = 0):
        '''Register a generator

        Arguments:
        generator -- Generator object
        priority -- Priority of generator
        '''

        if not isinstance(generator, GeneratorBase):
            raise TypeError("Invalid generator type (not subclass of GeneratorBase)")

        heapq.heappush(self._generators, (priority, generator))

    def generate(self, source, target):
        '''Try to generate source with each contained generator instance'''

        for pri, gen in self._generators:
            if gen.match(source):
                gen.generate(source, target)
                return

        raise ValueError("Source cannot be generated")

class ObjectGenerator(PriorityGenerator):
    '''The list of generators is extracted from the instance on start'''

    class Subgenerator(object):
        '''The ObjectGenerator scans for Subgenerators on instantiation

        Members:
        priority -- Priority of the generator
        '''

        priority = None

        def __init__(self, priority):
            self.priority = priority

        def bind(self, instance):
            '''Bind the subgenerator to the instance'''

            raise NotImplementedError('ObjectGenerator.Subgenerator.bind is abstract')

        def register(self, instance):
            '''Register subgenerator to the instance'''

            instance.register(self.bind(instance), priority = self.priority)

    class FunctionSubgenerator(Subgenerator):
        '''Object containing functions to be turned into generators

        Members:
        function -- Unbound function
        matcher -- Generator matcher
        '''

        function = None
        matcher = None

        def __init__(self, function, matcher, priority):
            super(FunctionSubgenerator, self).__init__(priority)

            self.function = function
            self.matcher = matcher

        def bind(self, instance):
            return FunctionGenerator(types.MethodType(self.function, instance), matcher = self.matcher)

    class TemplateSubgenerator(Subgenerator):
        '''Object containing functions to be turned into generators

        Members:
        template -- Template to use with rendering
        function -- Unbound binding-generator function
        matcher -- Generator matcher
        '''

        template = None
        function = None
        matcher = None

        def __init__(self, function, template, matcher, priority):
            super(FunctionSubgenerator, self).__init__(priority)

            self.function = function
            self.template = template
            self.matcher = matcher

        def bind(self, instance):
            return FunctionGenerator(self.template, types.MethodType(self.function, instance), matcher = self.matcher)

    class ObjectSubgenerator(Subgenerator):
        '''Object containing functions to be turned into generators

        Members:
        instance -- Generator instance
        '''

        instance = None

        def __init__(self, function, priority):
            super(ObjectGenerator, self).__init__(priority)

            self.function = function

        def bind(self, instance):
            return instance

    def __init__(self, matcher = None):
        super(ObjectGenerator, self).__init__(matcher = matcher)

        self._collect()

    def _collect(self):
        '''Collect subgenerators from instance'''

        for attr in dir(self):
            val = getattr(self, attr)

            if isinstance(val, ObjectGenerator.Subgenerator):
                val.register(self)

    @classmethod
    def function_generator(cls, matcher = None, priority = PriorityGenerator.PRI_BASE):
        '''Decorator to create a generator from a function'''

        def __decorator(func):
            return cls.FunctionSubgenerator(func, matcher, priority)

        return __decorator

    @classmethod
    def template_generator(cls, template, matcher = None, priority = PriorityGenerator.PRI_BASE):
        '''Decorator to create a generator from a template. The function is used to generate the bindings'''

        def __decorator(func):
            return cls.TemplateSubgenerator(func, template, matcher, priority)

        return __decorator

def match_tag(tag):
    def __matcher(source):
        return source.tag == tag

    return __matcher

def match_xpath(xpath):
    xpath = etree.XPath(xpath)

    def __matcher(source):
        return source in xpath(source)

    return __matcher

def match_all(source):
    return True

'''

class Lofasz(ObjectGenerator):
    @function_generator(match_tag('/foo/bar'))
    def gen_a(self, source, target):
        return str(source)

    @template_generator(match_all, priority = ObjectGenerator.PRI_FALLBACK)
    def generic(self, source):
        res = {}
        res['source'] = source
        return res

'''
