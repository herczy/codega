from codega.visitor import VisitorBase
from codega.ordereddict import OrderedDict

REQUIRED = 0
OPTIONAL = 1

reserved_property_prefixes = set(('__', 'ast_'))


def is_reserved(name):
    for prefix in reserved_property_prefixes:
        if name.startswith(prefix):
            return True

    return False


class AstNodeBase(object):
    ast_location = None

    def __init__(self, *args, **kwargs):
        assert hasattr(self, 'ast_class_info')
        self.ast_class_info.map_properties(self, args, kwargs)

    def __str__(self):
        return "%s(%s)" % (self.ast_name, ', '.join('%s=%r' % (k, v) for k, v in self.ast_properties.items()))

    __repr__ = __str__


class Info(object):
    '''Stores information about an AST class'''

    def __init__(self, name, properties):
        self.__name = name
        self.__properties = OrderedDict(properties)

    @property
    def name(self):
        return self.__name

    @property
    def bases(self):
        return self.__bases

    @property
    def properties(self):
        return OrderedDict(self.__properties)

    def map_properties(self, obj, args, kwargs):
        res = OrderedDict()
        args = list(args)
        kwargs = dict(kwargs)

        for name, klass in self.__properties.iteritems():
            if kwargs and name in kwargs:
                res[name] = kwargs.pop(name)

            elif args:
                res[name] = args[0]
                del args[0]

            elif klass == OPTIONAL:
                res[name] = None

            else:
                raise ValueError("Cannot handle required argument %s" % name)

        setattr(obj, 'ast_properties', res)
        for key, value in res.iteritems():
            assert not hasattr(obj, key)
            setattr(obj, key, value)

    def get_class(self, metainfo):
        if not metainfo.has_class(self.__name):
            self.__create_class(metainfo)

        return metainfo.get_class(self.__name)

    def __create_class(self, metainfo):
        members = {}
        members['ast_class_info'] = self
        members['ast_name'] = self.__name

        return metainfo.define_class(self.__name, (AstNodeBase,), members)


class Metainfo(object):
    '''AST node-set meta information. Contains the AST node classes.'''

    def __init__(self, metaclass=type):
        self.__metaclass = metaclass
        self.__classes = {}

    def register(self, name, cls):
        self.__classes[name] = cls

    def get_class(self, name):
        return self.__classes[name]

    def has_class(self, name):
        return name in self.__classes

    def define_class(self, name, bases, members):
        cls = self.__metaclass(name, bases, members)
        self.register(name, cls)

        return cls


class AstVisitor(VisitorBase):
    '''AST specific visitor class. For AST classes the
    visitor will use the name of the class, for other
    types the MRO will be used as in the ClassVisitor.'''

    def aspects(self, node):
        return [node.ast_name]
