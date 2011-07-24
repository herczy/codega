'''Config file handler'''

import stat
import os, os.path
from lxml import etree
import logging

from source import XmlSource
from rsclocator import FileResourceLocator, FallbackLocator, ModuleLocator
from version import Version
from error import ResourceError, VersionMismatchError

def filetime(locator, fname):
    return os.stat(locator.find(fname))[stat.ST_MTIME]

class ConfigNodeBase(object):
    '''Base class for configuration nodes

    Members:
    parent -- Config node parent
    raw_xml -- Raw XML
    '''

    parent = None
    raw_xml = None

    def __init__(self, parent, xml):
        self.parent = parent
        self.raw_xml = xml
        self._parse()

    def _parse(self):
        '''Parse the XML'''

        raise NotImplementedError("ConfigNodeBase._parse is abstract")

    def check(self, **kwargs):
        '''Check if the given attributes'''

        for key, value in kwargs.iteritems():
            if getattr(self, key) != value:
                return False

        return True

class ConfigSettings(ConfigNodeBase):
    '''Settings defined in configuration'''

    _data = None

    def _parse(self):
        self._data = {}

        for child in self.raw_xml:
            if child.tag == 'entry':
                self._data[child.attrib['name']] = child.text

            elif child.tag == 'container':
                self._data[child.attrib['name']] = ConfigSettings(self, child)

    def __getattr__(self, name):
        return self._data[name]

class ConfigSource(ConfigNodeBase):
    '''Source definitions

    Members:
    name -- Name of the source (referenced by targets)
    filename -- Source file

    targets -- Related targets
    '''

    name = None
    filename = None
    targets = None

    def __init__(self, parent, xml):
        super(ConfigSource, self).__init__(parent, xml)

        self.targets = []

    def _parse(self):
        self.name = self.raw_xml.find('name').text
        relative_filename = self.raw_xml.find('filename').text
        self.filename = self.parent.locator.find(relative_filename)

        source_parser = self.raw_xml.find('parser')
        if source_parser is not None:
            self.module, self.parser = source_parser.text.split(':', 1)

        else:
            self.module = 'codega.source'
            self.parser = 'XmlSource'

    @property
    def mtime(self):
        try:
            return filetime(self.parent.locator, self.filename)

        except ResourceError:
            return 0

    @property
    def data(self):
        if not hasattr(self, '_data_raw'):
            module = self.parent.locator.import_module(self.module)
            parser = getattr(module, self.parser)
            self._data_raw = parser().load(filename = self.filename, locator = self.parent.locator).getroot()

        return self._data_raw

    def add_target(self, target):
        self.targets.append(target)

class ConfigTarget(ConfigNodeBase):
    '''Target definitions'''

    sourceref = None

    def _parse(self):
        self.source = self.raw_xml.find('source').text

        settings_xml = self.raw_xml.find('settings')
        if settings_xml is not None:
            self.settings = ConfigSettings(self, settings_xml)

        else:
            self.settings = ConfigSettings(self, etree.Element('settings'))

        self.generator = self.raw_xml.find('generator').text
        self.module, self.gentype = self.generator.split(':', 1)

        self.target = self.raw_xml.find('target').text

    @property
    def mtime(self):
        try:
            return filetime(self.parent.write_locator, self.target)

        except ResourceError:
            return 0

class Config(object):
    '''Configuration object

    Members:
    _logger -- Config logger
    _config_locator -- File resource locators
    _write_locator -- Write locator
    _system_locator -- System locator (last priority)
    _raw_xml -- The unmodified source XML
    _version -- Configuration version, should be checked if changed
    _sources -- Dictionary of source entries
    _targets -- List of target entries
    _copy_list -- List of files to copy (from _config_locator)

    Static members:
    CURRENT_VERSION -- Current config version
    DEPRECATED_VERSION -- Versions below this are considered deprecated, they aren't supported
    '''

    CURRENT_VERSION = Version.load_from_string('1.0')
    DEPRECATED_VERSION = Version.load_from_string('0')

    _logger = None

    _config_locator = None
    _write_locator = None
    _system_locator = None
    _locator = None

    _raw_xml = None
    _version = None

    _sources = None
    _targets = None
    _copy_list = None

    def __init__(self, config_source, system_locator = None):
        self._logger = logging.getLogger('config')

        self._sources = []
        self._targets = []
        self._copy_list = []

        self._config_locator = FallbackLocator()
        self._write_locator = None
        self._system_locator = system_locator if system_locator is not None else FileResourceLocator()

        self._locator = FallbackLocator()
        self._locator.add_locator(self._config_locator)
        self._locator.add_locator(self._system_locator)

        self._raw_xml = config_source
        self._version = Version.load_from_string(self._raw_xml.get('version', '1.0'))

        self._logger.debug('Validating config XML')
        XmlSource().validate(self._raw_xml, filename = 'config.xsd', locator = ModuleLocator(__import__(__name__)))

        self._logger.debug('Checking version of config (current=%s minimal=%s maximal=%s)', self._version, Config.DEPRECATED_VERSION, Config.CURRENT_VERSION)
        if self._version > Config.CURRENT_VERSION:
            raise VersionMismatchError("Configuration is more recent than supported")

        if self._version <= Config.DEPRECATED_VERSION:
            raise VersionMismatchError("Configuration format deprecated")

        for entry in self._raw_xml:
            if entry.tag == 'paths':
                for path in entry:
                    if path.tag == 'target':
                        self._logger.debug('Set target path: %r', path.text)
                        self._write_locator = FileResourceLocator(self._system_locator.find(path.text))
                        self._locator.add_locator(self._write_locator, index = 0)

                    elif path.tag == 'path':
                        self._logger.debug('Added search path: %r', path.text)
                        self._config_locator.add_locator(FileResourceLocator(self._system_locator.find(path.text)))

            elif entry.tag == 'source':
                self._sources.append(ConfigSource(self, entry))

            elif entry.tag == 'target':
                self._targets.append(ConfigTarget(self, entry))

        # We should always check this from the XSD, so here we only
        assert self._write_locator is not None

        self._logger.debug('Cross-referencing sources and targets')
        for target in self.targets:
            source = list(self.find_source(name = target.source))

            # Note: these will be validated in the XSD
            if len(source) == 0:
                raise ConfigError('Cannot find source %s' % target.source)

            if len(source) > 1:
                raise ConfigError('Config contains more than one source %s' % target.source)

            source = source[0]

            # Resolve dependencies
            source.add_target(target)
            target.sourceref = source

            self._logger.debug('Source %s paired with target %r', source.name, target.source)

    @staticmethod
    def load(name, parser = XmlSource):
        base_path = os.path.abspath(os.path.dirname(name))
        config_name = os.path.basename(name)

        system_locator = FileResourceLocator(base_path)
        raw_config = parser().load(filename = config_name, locator = system_locator).getroot()

        logging.debug('Loading config %r with parser %r (base search path = %r)', name, parser.__name__, base_path)
        return Config(raw_config, system_locator = system_locator)

    @property
    def locator(self):
        return self._locator

    @property
    def write_locator(self):
        return self._write_locator

    @property
    def sources(self):
        return self._sources

    @property
    def targets(self):
        return self._targets

    @property
    def copy_list(self):
        return self._copy_list

    def find_source(self, **kwargs):
        for entry in self.sources:
            if entry.check(**kwargs):
                yield entry

    def find_target(self, **kwargs):
        for entry in self.targets:
            if entry.check(**kwargs):
                yield entry

    def find_need_rebuild(self):
        import codega
        modloc = ModuleLocator(codega)
        basetime = 0

        for rsc in modloc.list_resources():
            basetime = max(basetime, filetime(modloc, rsc))

        for target in self.targets:
            target_mt = target.mtime
            source_mt = target.sourceref.mtime

            if (source_mt > target_mt) or (basetime > target_mt):
                yield target
