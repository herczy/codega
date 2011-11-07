'''Base generator class. All other generators are derived from these generators'''

from codega.decorators import abstract

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
