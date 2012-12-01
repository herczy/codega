'''
Define handlers in a declarative manner, that is a class defined will do the handling.
Registering is automatic.
'''

from codega.generator.priority import PriorityGenerator, PRI_BASE
from codega.generator.base import GeneratorBase


def create_declarative_metaclass(base=type):
    '''
    Create a metatype for handlers. All handlers with this metatype
    will be collected.
    '''

    class __declarative(base):
        __collection__ = []

        def __new__(cls, name, bases, members):
            result = type.__new__(cls, name, bases, members)

            # Base classes won't get registered
            if not members.get('__base__', False):
                cls.__collection__.append(result)

            return result

    return __declarative


def collection(cls):
    '''
    Get the collection of a class or metaclass.
    '''

    if issubclass(cls, type):
        return cls.__collection__

    elif isinstance(cls, type):
        return collection(cls.__metaclass__)

    elif isinstance(cls, object):
        return collection(cls.__class__)

    else:
        raise TypeError("Invalid argument type")


class Generator(GeneratorBase):
    '''
    Subgenerator of a main generator.
    '''

    def __init__(self, parent):
        self.__parent = parent

        super(Generator, self).__init__()

    @property
    def parent(self):
        return self.__parent


class MainGenerator(PriorityGenerator):
    '''
    Priority generator for declarative sub-generators.
    '''

    def __init__(self, metaclass):
        '''
        Initialize metaclass.
        '''

        super(MainGenerator, self).__init__()

        for cls in collection(metaclass):
            if not issubclass(cls, Generator):
                raise TypeError("Only declarative sub-generators may be used with the main generator")

            # Find out priority
            priority = getattr(cls, '__priority__', PRI_BASE)

            # Find out the matcher
            matcher = getattr(cls, '__matcher__', None)

            # Create instance and register it
            instance = cls(self)
            self.register(instance, priority=priority, matcher=matcher)
