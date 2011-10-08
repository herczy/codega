from error import AstNodeError

class AstType(type):
    def __new__(cls, name, bases, members):
        def collect(attribute, update_set = lambda p, q: p.update(q), init_set = set):
            def update(what, value):
                if value is not None:
                    update_set(what, value)

            res = init_set()
            for cls in bases:
                for base in reversed(cls.__mro__):
                    update(res, getattr(base, attribute, None))

            update(res, members.pop(attribute, None))
            members[attribute] = res

        collect('_required')
        collect('_optional')
        collect('_validate', init_set = dict)

        return type.__new__(cls, name, bases, members)

class AstBase(object):
    '''
    Base class for AST nodes

    Members:
    _required -- List of required keys
    _optional -- List of optional keys
    _validate -- List of validators for a given key
    '''

    __metaclass__ = AstType

    _required = None
    _optional = None
    _validate = None

    def __init__(self, **kwargs):
        # Check if all required items are initialized
        req_missing = set(self._required).difference(set(kwargs.keys()))
        if req_missing:
            raise AstNodeError("Missing AST keys (%s) from AST node %s" % (', '.join(map(repr, req_missing)), self.__class__.__name__))

        # Check if there are no keys outside of the optional list
        extra = set(kwargs.keys()).difference(self._required).difference(self._optional)
        if extra:
            raise AstNodeError("Unknown AST keys (%s) in AST node %s" % (', '.join(map(repr, extra)), self.__class__.__name__))

        # Check if the specifications in validate are met
        for key, validator in self._validate.iteritems():
            if not kwargs.has_key(key):
                continue

            if not validator(kwargs[key]):
                raise AstNodeError("Key %s does not meet specifications in AST node %s" % (key, self.__class__.__name__))

        for key, value in kwargs.iteritems():
            setattr(self, key, value)

        for key in set(self._optional).difference(set(kwargs.keys())):
            setattr(self, key, None)

    def __values(self):
        values = []

        for req in self._required:
            values.append('%s=%r' % (req, getattr(self, req)))

        for opt in self._optional:
            val = getattr(self, opt)
            if val is None:
                continue

            values.append('%s=%r' % (opt, val))

        return values

    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__, ', '.join(self.__values()))

    __repr__ = __str__
