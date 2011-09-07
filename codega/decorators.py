'''Various commonly used function decorators'''

def abstract(func):
    '''The class method is an abstract.

    Arguments:
    func -- Decorated function. Will never be called
    '''

    def __wrapper(self, *args, **kwargs):
        raise NotImplementedError("%s.%s is an abstract method" % (self.__class__.__name__, func.__name__))

    __wrapper.__name__ = func.__name__
    __wrapper.__doc__ = func.__doc__

    return __wrapper

def init_mark(func):
    '''Init markings on function'''

    if not hasattr(func, '__marks__'):
        func.__marks__ = {}

def set_mark(func, mark_type, mark_value):
    '''Mark a function with some value.

    This is useful if the function needs to have some distinct identifier
    for easier identification.

    Arguments:
    func -- Function to be marked
    mark_type -- Mark type. A function may only be marked with a type once.
                 If attempted more than one time, an error is raised.
    mark_value -- Mark value. Can be checked against
    '''

    init_mark(func)

    if func.__marks__.has_key(mark_type):
        raise RuntimeError("Function %s has already been marked with %s" % (func.__name__, mark_type))

    func.__marks__[mark_type] = mark_value

def copy_marks(dest, src):
    '''Copy the marks on src to dest'''

    init_mark(dest)

    if hasattr(src, '__marks__'):
        dest.__marks__.update(src.__marks__)

def mark(mark_type, mark_value):
    '''Decorator wrapper for set_mark

    Arguments:
    mark_type -- Mark type. A function may only be marked with a type once.
                 If attempted more than one time, an error is raised.
    mark_value -- Mark value. Can be checked against
    '''

    def __decorator(func):
        set_mark(func, mark_type, mark_value)
        return func

    return __decorator

def has_mark(func, mark_type):
    '''Check if the function has been marked with the given type'''

    return getattr(func, '__marks__', {}).has_key(mark_type)

def get_mark(func, mark_type):
    '''Return the value of the given mark'''

    if not has_mark(func, mark_type):
        raise AttributeError("The function %s has no mark %s" % (func.__name__, mark_type))

    return func.__marks__[mark_type]

def get_mark_default(func, mark_type, default = None):
    '''Return the value of the given mark or default if mark is not found'''

    if not has_mark(func, mark_type):
        return default

    return func.__marks__[mark_type]

def collect_marked(functions, mark_type, mark_value = None):
    '''Collect all functions marked in the dictionary.

    Arguments:
    functions -- A dictionary to collect from
    mark_type -- Mark type of the functions.
    mark_value -- If set, only the marks with the given value will be returned
    '''

    for value in functions.values():
        if not hasattr(value, '__call__'):
            continue

        if not has_mark(value, mark_type):
            continue

        mark = get_mark(value, mark_type)
        if mark_value is not None and mark != mark_value:
            continue

        yield mark, value

def collect_marked_bound(obj, *args, **kwargs):
    '''Collect all methods marked bound to the object'''

    return collect_marked(dict((k, getattr(obj, k)) for k in dir(obj)), *args, **kwargs)
