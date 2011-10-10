from codega.decorators import mark

from base import AstBase

def validator(name):
    '''Define a validator'''

    return mark('validator', name)

def type_validator(name, type):

    @validator(name)
    def __validator(value):
        return isinstance(value, type)

    return __validator

v_string = type_validator('string', basestring)
v_int = type_validator('int', int)
v_bool = type_validator('bool', bool)
v_float = type_validator('float', float)
v_tuple = type_validator('tuple', tuple)
v_list = type_validator('list', list)
v_set = type_validator('set', set)
v_AstBase = type_validator('AstBase', AstBase)

@validator('any')
def v_any(value):
    return True

@validator('nothing')
def v_nothing(value):
    return False

def collection(validator, min = None, max = None, exact = None):

    def __validator(value):
        if not hasattr(value, '__len__'):
            return False

        if len(value) > 0 and not reduce(lambda p, q: p and q, map(validator, value)):
            return False

        if exact is not None:
            return len(value) == exact

        if min is not None and len(value) < min:
            return False

        if max is not None and len(value) > max:
            return False

        return True

    return __validator

def v_negate(validator):

    def __validator(value):
        return not validator(value)

    return __validator

def v_or(v1, v2):

    def __validator(value):
        return v1(value) or v2(value)

    return __validator

def v_and(v1, v2):

    def __validator(value):
        return v1(value) and v2(value)

    return __validator

@validator('classname')
def v_classname(clsname):

    def __validator(value):
        return value.__class__.__name__ == clsname

    return __validator

@validator('fromcls')
def v_fromcls(*clsnames):

    def __validator(value):
        for base in value.__class__.__mro__:
            if base.__name__ in clsnames:
                return True

        return False

    return __validator

@validator('in')
def v_in(*set):

    def __validator(value):
        return value in set

    return __validator
