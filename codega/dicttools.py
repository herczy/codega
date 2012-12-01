'''Dictionary tools to handle template arguments better'''


def dict_from_element(element, base=None):
    '''Return a dictionary copy of element.attrib. Use base as
    the base dictionary'''

    res = {}
    if base:
        res.update(base)

    res.update(element.attrib)
    return res


def map_keys(func, base):
    '''Call func for each key in base'''

    return dict((func(k), base[k]) for k in base.keys())


def map_values(func, base):
    '''Call func for each value in base'''

    return dict((k, func(base[k])) for k in base.keys())


def filter_by_keys(filt, base):
    '''Filter keys from dict by the filt function'''

    keys = filter(filt, base.keys())
    return dict((k, base[k]) for k in keys)


def filter_keys(base, *keywords):
    '''Only include keys in keyword'''

    return filter_by_keys(lambda k: k in keywords, base)


def exclude_internals(base):
    '''Exclude keywords typically reserved for Python from the dictionary'''

    def __filter(key):
        if key[:2] == '__':
            return False

        if key in ('self',):
            return False

        return True

    return filter_by_keys(__filter, base)


def bindict(source, context, **bind):
    '''Create a dict from the context, source and other keywords'''

    res = dict(bind)
    res.update(map_keys(lambda k: 'attr_%s' % k, dict_from_element(source)))
    res['arg_context'] = context
    res['arg_source'] = source

    return exclude_internals(res)


def autobindict(func):
    '''Translate typical template arguments into a contextualized version'''

    def __wrapper(self, source, context):
        bindings = bindict(source, context)
        ret = func(self, source, context, bindings)
        if ret is not None:
            bindings.update(exclude_internals(ret))

        return bindings

    __wrapper.__name__ = func.__name__
    __wrapper.__doc__ = func.__doc__
    return __wrapper
