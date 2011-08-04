'''Various commonly used function decorators'''

def abstract(func):
    '''Mark a class method as an abstract.

    Arguments:
    func -- Decorated function. Will never be called
    '''

    def __wrapper(self, *args, **kwargs):
        raise NotImplementedError("%s.%s is an abstract method" % (self.__class__.__name__, func.__name__))

    __wrapper.__name__ = func.__name__
    __wrapper.__doc__ = func.__doc__

    return __wrapper
