'''
Priority generators are composite generators using a list of sub-generators registered to
render the current source.

Special constants:
PRI_HIGHEST -- Highest priority
PRI_HIGH -- High priority
PRI_BASE -- Base priority
PRI_LOW -- Low priority
PRI_LOWEST -- Lowest priority
PRI_FALLBACK -- Fallback priority
'''

import heapq

from codega import logger

from base import GeneratorBase

PRI_HIGHEST = -100
PRI_HIGH = -10
PRI_BASE = 0
PRI_LOW = 10
PRI_LOWEST = 100
PRI_FALLBACK = 1000

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

    def get_handler(self, source, context):
        '''Try to generate source with each contained generator instance'''

        heap = list(self._generators)

        while heap:
            _, (gen, matcher) = heapq.heappop(heap)

            if matcher is None or matcher(source, context):
                logger.debug('Generating source %r with priority generator %r (matching sub-generator %r)' % (source, self, gen))
                return gen

        raise ValueError("Source cannot be generated")

    def generate(self, source, context):
        return self.get_handler(source, context)(source, context)
