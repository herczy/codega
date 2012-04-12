from codega.visitor import VisitorBase
from codega.ordereddict import OrderedDict

REQUIRED = 0
OPTIONAL = 1

class Property(object):
    def __init__(self, name, klass=REQUIRED):
        self.name = name
        self.klass = klass

    @staticmethod
    def get_class_value(value):
        if value == 'required':
            return REQUIRED

        elif value == 'optional':
            return OPTIONAL

        raise ValueError("Invalid property class")

class PropertySet(OrderedDict):
    def __init__(self, entries, args, kwargs):
        super(PropertySet, self).__init__()

        self._enties = entries

        args = list(args)
        kwargs = dict(kwargs)
        for prop in entries:
            if kwargs and prop.name in kwargs:
                self[prop.name] = kwargs.pop(prop.name)

            elif args:
                self[prop.name] = args[0]
                del args[0]

            elif prop.klass == OPTIONAL:
                self[prop.name] = None

            else:
                raise ValueError("Cannot handle required argument %s" % prop.name)

    def __getattr__(self, key):
        if key[0] == '_':
            return super(PropertySet, self).__getattribute__(key)

        return self[key]

class Metainfo(object):
    def __init__(self):
        self._classes = {}

    def register(self, cls):
        self._classes[cls.name] = cls

    @property
    def classes(self):
        for name, cls in self._classes.items():
            yield name, cls

def create_meta_class(metainfo=None, base=type):
    class NodeType(type):
        metainfo = None

        def __new__(cls, name, bases, members):
            # Default name of the AST node is the class name
            members.setdefault('name', name)

            # Property parsing
            properties = members.pop('property_definitions', ())
            if isinstance(properties, basestring):
                properties = (s.strip() for s in properties.split(';'))

                prop_result = []
                for prop in properties:
                    if isinstance(prop, basestring):
                        klass, name = filter(lambda s: len(s) > 0, (s.strip() for s in prop.split(' ')))
                        klass = Property.get_class_value(klass)

                        prop_result.append(Property(name, klass=klass))

            else:
                prop_result = properties

            members['property_definitions'] = prop_result

            # Rules are processed later, here we just ensure they exist
            members.setdefault('rules', ())

            # Set the metainfo class
            members['metainfo'] = cls.metainfo

            # Create class and register to the metainfo object if it's not a base class
            members.setdefault('base', False)
            res = type.__new__(cls, name, bases, members)

            if not members['base']:
                cls.metainfo.register(res)

            return res

    if not metainfo:
        metainfo = Metainfo()
    NodeType.metainfo = metainfo
    return NodeType

def create_base_node(name, base=object, metainfo=None, metatype=type):
    metatype = create_meta_class(metainfo=metainfo, base=metatype)

    class NodeBase(base):
        __metaclass__ = metatype

        base = True
        properties = None

        def __init__(self, *args, **kwargs):
            self.properties = PropertySet(self.property_definitions, args, kwargs)

            super(NodeBase, self).__init__()

        def map(self, func):
            for key, value in self.properties.items():
                yield key, func(key, value)

        @classmethod
        def subclass(cls, name, **kwargs):
            return cls.__metaclass__(name, (cls,), kwargs)

        def __str__(self):
            return '%s(%s)' % (self.name, '; '.join('%s=%r' % p for p in self.properties.items()))

        def __repr__(self):
            return '%s(%s)' % (self.__class__.__name__, '; '.join('%s=%r' % p for p in self.properties.items()))

    return NodeBase

class AstVisitor(VisitorBase):
    def aspects(self, node):
        if hasattr(node, 'metainfo'):
            return [ node.name ]

        else:
            return node.__class__.__mro__
