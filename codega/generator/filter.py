'''
Filter generators process the output of some other generators with the help of
the filter function list. Each function is applied subsequently.
'''

from function import FunctionGenerator

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
