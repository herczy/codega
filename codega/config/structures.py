import os
import re

from codega.ordereddict import OrderedDict, DictMixin
from codega.config import latest_version
from codega.version import Version

module_validator = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$')
classname_validator = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

def config_property(name, property_type=basestring, enable_change=True):
    if enable_change:
        def setter(self, value):
            if not isinstance(value, property_type):
                raise TypeError("Config attributes can only be of class %s" % property_type.__class__)

            setattr(self, name, value)

        def deleter(self):
            setattr(self, name, None)

    else:
        def setter(self, value):
            raise AttributeError("Attribute cannot be set")

        def deleter(self):
            raise AttributeError("Attribute cannot be deleted")

    def getter(self):
        return getattr(self, name)

    return property(getter, setter, deleter)

class NodeBase(object):
    '''Base class for configuration nodes

    Members:
    _parent -- Config node parent
    '''

    _parent = None
    parent = property(lambda self: self._parent)

    @property
    def root(self):
        if self._parent is not None:
            return self._parent.root

        return self

    def __init__(self, parent):
        self._parent = parent

class Settings(NodeBase, DictMixin):
    '''Target settings.

    Uses a recursive container as data but it is not one. This is so because
    we want to avoid having double inheritance (other than with mixins).

    Members:
    _data -- The recursive container
    '''

    _data = None

    class RecursiveContainer(OrderedDict):
        '''Implements a recursive container. The keys are ordered'''
        data = config_property('_data', enable_change=False)

        def __setitem__(self, key, value):
            if not isinstance(key, basestring):
                raise KeyError("RecursiveContainer can only have string keys")

            if not isinstance(value, basestring) and not isinstance(value, Settings.RecursiveContainer):
                raise TypeError("RecursiveContainer can only contain RecursiveContainers and strings")

            super(Settings.RecursiveContainer, self).__setitem__(key, value)

        def add_container(self, key):
            self[key] = Settings.RecursiveContainer()
            return self[key]

        __getattr__ = OrderedDict.__getitem__

    data = config_property('_data', enable_change=False)

    @property
    def empty(self):
        return len(self._data) == 0

    def __init__(self, parent):
        super(Settings, self).__init__(parent)

        self._data = Settings.RecursiveContainer()

    def add_container(self, key):
        return self._data.add_container(key)

    def __getitem__(self, key):
        return self._data.__getitem__(key)

    def __setitem__(self, key, value):
        self._data.__setitem__(key, value)

    def __delitem__(self, key):
        self._data.__delitem__(key)

    __getattr__ = __getitem__

class ModuleReference(NodeBase):
    '''Refers to a class that's used by the config

    Members:
    _module -- Module the entry is referring to
    _reference -- Class reference in the module

    _module_def -- Default module
    _reference_def -- Default reference
    '''

    _module = None
    _reference = None

    _module_def = None
    _reference_def = None

    @property
    def module(self):
        if self._module is None:
            return self._module_def

        return self._module

    @module.setter
    def module(self, value):
        if not isinstance(value, basestring):
            raise TypeError("Module name can only be string")

        if not module_validator.match(value):
            raise ValueError("Invalid module name")

        self._module = value

    @module.deleter
    def module(self):
        self._module = None

    @property
    def reference(self):
        if self._reference is None:
            return self._reference_def

        return self._reference

    @reference.setter
    def reference(self, value):
        if not isinstance(value, basestring):
            raise TypeError("Class name can only be string")

        if not classname_validator.match(value):
            raise ValueError("Invalid class name")

        self._reference = value

    @reference.deleter
    def reference(self):
        self._reference = None

    @property
    def is_default(self):
        return self._module is None or self._reference is None

    def __init__(self, parent, module_def=None, reference_def=None):
        super(ModuleReference, self).__init__(parent)

        self._module_def = module_def
        self._reference_def = reference_def

    def load(self, locator):
        return getattr(locator.import_module(self.module), self.reference)

    def load_from_string(self, string):
        # Old format: module and class are split with ':'
        if ':' in string:
            module, reference = string.rsplit(':', 1)

        # New format: first part is the module, last
        # part (after last period) is the class
        elif '.' in string:
            module, reference = string.rsplit('.', 1)

        else:
            raise ValueError("Invalid module reference %r" % string)

        # Save the module/reference values. This is here so if the setters
        # raise any error, we still have a consistent state.
        savestate = (self.module, self.reference)
        try:
            self.module, self.reference = module, reference

        except:
            self.module, self.reference = savestate
            raise

    def __str__(self):
        return '%s.%s' % (self.module, self.reference)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self)

class Source(NodeBase):
    '''Config source entry

    A source entry specifies the source filename, generator, etc.

    Members:
    _name -- Source name
    _parser -- Parser class reference
    _resource  -- Resource name
    _transform -- Transformation list
    '''

    _name = None
    _parser = None
    _resource = None
    _transform = None

    name = config_property('_name')
    parser = config_property('_parser', enable_change=False)
    resource = config_property('_resource')
    transform = config_property('_transform', enable_change=False)

    def __init__(self, parent):
        super(Source, self).__init__(parent)

        self._transform = []
        self._parser = ModuleReference(self, 'codega.source', 'XmlSource')

class Target(NodeBase):
    '''Config target entry

    Members:
    _source -- Target source reference (by name)
    _filename -- Target file name
    _generator -- Target generator
    _settings -- Target-specific settings
    '''

    _source = None
    _filename = None
    _generator = None
    _settings = None

    source = config_property('_source')
    filename = config_property('_filename')
    generator = config_property('_generator', enable_change=False)
    settings = config_property('_settings', enable_change=False)

    def __init__(self, parent):
        super(Target, self).__init__(parent)

        self._settings = Settings(self)
        self._generator = ModuleReference(self)

class Copy(NodeBase):
    '''Copy target entry

    Members:
    _source -- Source file name
    _target -- Destination file name
    '''

    _source = None
    _target = None

    source = config_property('_source')
    target = config_property('_target')

class PathList(NodeBase):
    '''List of paths

    Members:
    _destination -- Destination directory
    _paths -- Search paths
    '''

    _destination = None
    _paths = None

    destination = config_property('_destination')
    paths = config_property('_paths', enable_change=False)

    def __init__(self, parent):
        super(PathList, self).__init__(parent)

        self._destination = '.'
        self._paths = []

class Config(NodeBase):
    '''Complete configuration

    Members:
    _version -- Config version
    _paths -- Path list
    _sources -- Dict of sources
    _targets -- Dict of targets
    _external -- List of external build dependencies

    _dependencies -- Dependencies between targets and sources
    '''

    class SourceCollection(OrderedDict):
        '''Source list, checks for types and possible dependencies'''

        def __init__(self, parent):
            super(Config.SourceCollection, self).__init__()

            self._parent = parent

        def __setitem__(self, key, value):
            if not isinstance(value, Source):
                raise TypeError("Cannot add non-source objects to source list")

            value.name = key
            super(Config.SourceCollection, self).__setitem__(key, value)

        def __getitem__(self, key):
            try:
                return super(Config.SourceCollection, self).__getitem__(key)

            except KeyError:
                raise KeyError("Source %s not found" % key)

        def __delitem__(self, key):
            if key in self._parent._dependencies.values():
                raise KeyError("Source %s can not be deleted, it has dependencies" % key)

            del self._sources[key]

    class TargetCollection(OrderedDict):
        '''Target list, checks for types and possible dependencies'''

        def __init__(self, parent):
            super(Config.TargetCollection, self).__init__()

            self._parent = parent

        def __setitem__(self, key, value):
            if not isinstance(value, Target):
                raise TypeError("Cannot add non-source objects to source list")

            if not self._parent.sources.has_key(value.source):
                raise KeyError("Source %s does not exist" % value.source)

            value.name = key
            super(Config.TargetCollection, self).__setitem__(key, value)
            self._parent._dependencies[value.filename] = value.source

        def __delitem__(self, key):
            del self._parent._dependencies[self._targets[key]]
            del self._targets[key]

        def __getitem__(self, key):
            try:
                return super(Config.TargetCollection, self).__getitem__(key)

            except KeyError:
                raise KeyError("Target %s not found" % key)

    _version = None
    _paths = None
    _sources = None
    _targets = None
    _copy = None
    _external = None

    _dependencies = None

    paths = config_property('_paths', enable_change=False)
    sources = config_property('_sources', enable_change=False)
    targets = config_property('_targets', enable_change=False)
    copy = config_property('_copy', enable_change=False)
    external = config_property('_external', enable_change=False)

    @property
    def version(self):
        return self._version.dup()

    @version.setter
    def version(self, value):
        if isinstance(value, Version):
            version = value.dup()

        elif isinstance(value, basestring):
            try:
                version = Version.load_from_string(value)

            except Exception:
                raise ValueError("Invalid version string %r" % value)

        else:
            raise ValueError("Version can only be a string or another Version object")

        self._version = version

    def __init__(self):
        super(Config, self).__init__(None)

        self._version = latest_version.dup()
        self._paths = PathList(self)
        self._sources = Config.SourceCollection(self)
        self._targets = Config.TargetCollection(self)
        self._copy = OrderedDict()
        self._external = []
        self._dependencies = {}


class StructureBuilder(object):
    def __init__(self):
        self.__config = Config()
        self.__config.paths.destination = '.'
        self.__config.version = latest_version

    @property
    def config(self):
        return self.__config

    def add_source(self, name, resource, parser=None, transform=()):
        # Create source object
        source = Source(self.__config)
        source.name = name
        source.resource = resource
        if parser is not None:
            source.parser.load_from_string(parser)

        for trans in transform:
            transform_module = ModuleReference(source)
            transform_module.load_from_string(trans)
            source.transform.append(transform_module)

        self.__config.sources[source.name] = source

        return source

    def add_target(self, source, filename, generator):
        # Create target object
        target = Target(self.__config)
        target.source = source
        target.filename = filename
        target.generator.load_from_string(generator)

        self.__config.targets[target.filename] = target

        return target

    def add_copy(self, source, target):
        copy = Copy(self.__config)
        copy.source = source
        copy.target = target

        self.__config.copy[copy.target] = copy

        return copy

    def add_external(self, config):
        self.__config.external.append(config)

    def set_destination(self, path):
        self.__config.paths.destination = path

    def add_include(self, path):
        self.__config.paths.paths.append(path)

    def add_setting(self, target, key, value):
        if isinstance(target, basestring):
            target = self.__config.targets[target]

        if isinstance(key, basestring):
            key = key.split('.')

        if '' in key:
            raise RuntimeError('Empty key component found')

        if len(key) == 0:
            raise RuntimeError('Empty key found')

        actual = target.settings
        for index, component in enumerate(key[:-1]):
            if component not in actual:
                actual[component] = Settings.RecursiveContainer()

            elif not isinstance(actual[component], Settings.RecursiveContainer):
                raise RuntimeError("Key %r is not a container" % '.'.join(key[:index]), 0)

            actual = actual[component]

        if key[-1] in actual:
            raise RuntimeError("Key %r already exists in settings" % '.'.join(key[-1]), 0)

        actual[key[-1]] = value
