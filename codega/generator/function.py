'''
A function generator is a generator that calls a function for the generation.
'''

from base import GeneratorBase

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
