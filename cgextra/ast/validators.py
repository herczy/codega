from base import AstBase

validators = {}

def validator(name):
    '''Define a validator'''

    def __decorator(func):
        global validators

        validators[name] = func
        return func

    return __decorator

def type_validator(name, type):

    @validator(name)
    def __validator(value):
        return isinstance(value, type)

type_validator('string', basestring)
type_validator('int', int)
type_validator('bool', bool)
type_validator('float', float)
type_validator('tuple', tuple)
type_validator('list', list)
type_validator('set', set)
type_validator('AstBase', AstBase)

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

@validator('from')
def v_from(*clsnames):

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
