import re

from lxml import etree

import logger
from error import *
from ordereddict import OrderedDict, DictMixin
from visitor import *
from source import XmlSource, validate_xml
from rsclocator import ModuleLocator
from version import Version
from bzrlib.util.configobj.configobj import ParseError

module_validator = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$')
classname_validator = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
latest_version = Version(1, 1)

def config_property(name, property_type = basestring, enable_change = True):
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

        def deleter(self, value):
            raise AttributeError("Attribute cannot be deleted")

    def getter(self):
        return getattr(self, name)

    return property(getter, setter, deleter)

def build_element(tag, attributes = {}, text = '', children = []):
    res = etree.Element(tag)
    res.text = text
    for k, v in attributes.iteritems():
        res.attrib[k] = v
    res.extend(children)
    return res

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
        data = config_property('_data', enable_change = False)

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

    data = config_property('_data', enable_change = False)

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

    def __init__(self, parent, module_def = None, reference_def = None):
        super(ModuleReference, self).__init__(parent)

        self._module_def = module_def
        self._reference_def = reference_def

    def load(self, locator):
        return getattr(locator.import_module(self.module), self.reference)

    def load_from_string(self, string):
        if ':' not in string:
            raise ValueError("Invalid module reference %s" % string)

        # Keep the previous state if invalid
        state = (self._module, self._reference)
        try:
            self.module, self.reference = string.split(':')

        except:
            self._module, self._reference = state
            raise

    def __str__(self):
        return '%s:%s' % (self.module, self.reference)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self)

class Source(NodeBase):
    '''Config source entry

    A source entry specifies the source filename, generator, etc.

    Members:
    _name -- Source name
    _parser -- Parser class reference
    _resource  -- Resource name
    '''

    _name = None
    _parser = None
    _resource = None

    name = config_property('_name')
    parser = config_property('_parser', enable_change = False)
    resource = config_property('_resource')

    def __init__(self, parent):
        super(Source, self).__init__(parent)

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
    generator = config_property('_generator', enable_change = False)
    settings = config_property('_settings', enable_change = False)

    def __init__(self, parent):
        super(Target, self).__init__(parent)

        self._settings = Settings(self)
        self._generator = ModuleReference(self)

class PathList(NodeBase):
    '''List of paths

    Members:
    _destination -- Destination directory
    _paths -- Search paths
    '''

    _destination = None
    _paths = None

    destination = config_property('_destination')
    paths = config_property('_paths', enable_change = False)

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

            except KeyError, e:
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

            except KeyError, e:
                raise KeyError("Target %s not found" % key)

    _version = None
    _paths = None
    _sources = None
    _targets = None
    _dependencies = None
    paths = config_property('_paths', enable_change = False)
    sources = config_property('_sources', enable_change = False)
    targets = config_property('_targets', enable_change = False)

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

            except Exception, e:
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
        self._dependencies = {}

class ParseVisitor(ClassVisitor):
    '''Parse the configs XML tree representation to the internal representation.'''

    def __init__(self):
        super(ParseVisitor, self).__init__()

        self._current_node = None

    def visit(self, node, xml_node):
        self._current_node = xml_node
        try:
            super(ParseVisitor, self).visit(node, xml_node)

        except Exception, e:
            if isinstance(e, ParseError):
                raise

            logger.error("Exception caught: %s" % e)
            raise ParseError("XML entry invalid (see line %s)" % self._current_node.sourceline)

    @visitor(ModuleReference)
    def module_reference(self, node, xml_node):
        node.load_from_string(xml_node.text)

    @visitor(Source)
    def source(self, node, xml_node):
        node.name = xml_node.find('name').text
        node.resource = xml_node.find('resource').text

        parser = xml_node.find('parser')
        if parser is not None:
            self.visit(node.parser, parser)

    @visitor(Settings.RecursiveContainer)
    def recursive_container(self, node, xml_node):
        for chld in xml_node:
            if chld.tag == 'entry':
                node[chld.attrib['name']] = chld.text

            else:
                new_node = node[chld.attrib['name']] = Settings.RecursiveContainer()
                self.visit(new_node, chld)

    @visitor(Settings)
    def settings(self, node, xml_node):
        self.visit(node.data, xml_node)

    @visitor(Target)
    def target(self, node, xml_node):
        node.source = xml_node.find('source').text
        node.filename = xml_node.find('target').text
        self.visit(node.generator, xml_node.find('generator'))

        settings_xml = xml_node.find('settings')
        if settings_xml is not None:
            self.visit(node.settings, settings_xml)

    @visitor(PathList)
    def path_list(self, node, xml_node):
        for chld in xml_node:
            if chld.tag == 'target':
                node.destination = chld.text

            else:
                node.paths.append(chld.text)

    @visitor(Config)
    def config(self, node, xml_node):
        node.version = xml_node.attrib['version']
        for chld in xml_node:
            if chld.tag == 'paths':
                self.visit(node.paths, chld)

            elif chld.tag == 'source':
                source = Source(node)
                self.visit(source, chld)
                node.sources[source.name] = source

            elif chld.tag == 'target':
                target = Target(node)
                self.visit(target, chld)
                node.targets[target.filename] = target

class SaveVisitor(ClassVisitor):
    '''Parse the internal config representation into an XML tree representation'''

    @visitor(ModuleReference)
    def module_reference(self, node):
        return '%s:%s' % (node.module, node.reference)

    @visitor(Source)
    def source(self, node):
        res = build_element('source', children = [
                  build_element('name', text = node.name),
                  build_element('resource', text = node.resource),
              ])

        if not node.parser.is_default:
            res.append(build_element('parser', text = self.visit(node.parser)))

        return res

    @visitor(Settings.RecursiveContainer)
    def recursive_container(self, node):
        res = []
        for name, value in node.iteritems():
            if isinstance(value, basestring):
                res.append(build_element('entry', attributes = { 'name' : name }, text = value))

            else:
                res.append(build_element('container', attributes = { 'name' : name }, children = self.visit(value)))

        return res

    @visitor(Settings)
    def settings(self, node):
        return build_element('settings', children = self.visit(node.data))

    @visitor(Target)
    def target(self, node):
        res = etree.Element('target')
        res.append(build_element('source', text = node.source))
        res.append(build_element('generator', text = self.visit(node.generator)))
        res.append(build_element('target', text = node.filename))
        res.append(self.visit(node.settings))

        return res

    @visitor(PathList)
    def path_list(self, node):
        res = build_element('paths')
        res.append(build_element('target', text = node.destination))
        for path in node.paths:
            res.append(build_element('path', text = path))

        return res

    @visitor(Config)
    def config(self, node):
        res = etree.Element('config')
        res.attrib['version'] = str(node.version)
        res.append(self.visit(node.paths))
        res.extend([self.visit(source) for source in node.sources.values()])
        res.extend([self.visit(target) for target in node.targets.values()])

        return res

class UpdateVisitor(ExplicitVisitor):
    '''To be able to handle different versions, we need to 'update' the
    current version. So if a new compatible config version appears we need
    to add an update function to that version.

    Since there is only one supported version, only the fallback and the current
    version visitors will be defined.

    The update must be done prior to validating the XML. So the XSD always validates
    the current version.

    Version history:
    * 1.0 -- Initial version
    * 1.1 -- Renamed /config/source/filename to /config/source/resource since in this
             version we accept non-file based sources too.
    '''

    @visitor(Version(1, 0))
    def update_1_0(self, version, xml_root):
        '''Update 1.0 configs to 1.1'''

        for node in xml_root.findall('source/filename'):
            node.tag = 'resource'
        xml_root.attrib['version'] = '1.1'
        return self.visit(Version(1, 1), xml_root)

    @visitor(latest_version)
    def version_current(self, version, xml_root):
        return xml_root

    def visit_fallback(self, version, xml_root):
        raise VersionMismatchError("Configs with version %s are not supported" % version)

def parse_config_file(filename):
    try:
        logger.debug('Loading config file %s', filename)

        # Initialize configuration object
        config = Config()

        # Parse raw XML file
        try:
            xml_root = XmlSource().load(filename).getroot()

        except Exception, e:
            raise ParseError("Could not load source XML: %s" % e, 0)

        # Update the XML tree if needed (this needs pre-verifying the version)
        if not xml_root.attrib.has_key('version'):
            raise ParseError("Configuration version cannot be determined", 1)

        try:
            version = Version.load_from_string(xml_root.attrib['version'])

        except ValueError:
            raise ParseError("Invalid version format %s" % xml_root.attrib['version'], 1)

        xml_root = UpdateVisitor().visit(version, xml_root)

        # Validate the XML root with the config.xsd. The config.xsd file always
        # refers to the current version (see UpdateVisitor.version_current)
        try:
            validate_xml(xml_root, resource = 'config.xsd', resource_locator = ModuleLocator(__import__(__name__)))

        except etree.DocumentInvalid, e:
            raise ParseError('Configuration is invalid', e.error_log.last_error.line)

        # Parse the XML structure
        visitor = ParseVisitor()
        try:
            visitor.visit(config, xml_root)

        except Exception, e:
            raise ParseError(str(e), visitor._current_node.sourceline)

        return config

    except Exception, e:
        raise
        if isinstance(e, ParseError):
            raise

        raise ParseError('Error detected during parsing: %s' % e, 0)

def save_config(config):
    try:
        return etree.tostring(SaveVisitor().visit(config), pretty_print = True)

    except Exception, e:
        raise SaveError('Error detected while saving the config: %s' % e)
