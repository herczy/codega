'''
Filter generators process the output of some other generators with the help of
the filter function list. Each function is applied subsequently.
'''

from codega.decorators import has_mark, set_mark, get_mark

from base import GeneratorError
from function import FunctionGenerator


class FilterError(GeneratorError):
    '''Raised when the filtering (or preparation) fails.'''


def add_filter(filter):
    '''
    Mark a function as having filters. This will be used when the FilterGenerator
    is constructed.
    '''

    def __decorator(func):
        if not has_mark(func, 'filters'):
            set_mark(func, 'filters', [])

        # Since the add_filter will mostly be used as a decorator and because decorators
        # are applied in reverse order (the closest one to the function definition gets
        # applied first) we should apply the new filter to the beginning of the list so
        # the filter statements are easier to read.
        get_mark(func, 'filters').insert(0, filter)

        return func

    return __decorator


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
    def factory(cls, subfactory=None):
        '''
        The sub-factory will be used to create a generator. The results of this generator will
        be used as the base of the filter.

        If no sub-factory is given, the function is used without any wrapping.
        '''

        def __decorator(func):
            if not has_mark(func, 'filters'):
                raise FilterError('The current function was marked as a %s yet it has no filters defined' % cls.__name__)

            generator = func
            if subfactory is not None:
                generator = subfactory(generator)

            # Collect the filter definitions, if there are any.
            return cls(generator, *get_mark(func, 'filters'))

        return __decorator
