'''Config file handler'''

import stat
import os, os.path
from lxml import etree

import source
from rsclocator import FileResourceLocator, FallbackLocator, ModuleLocator
from version import Version
from error import ResourceError, VersionMismatchError

class ConfigSettings(object):
    '''Settings defined in configuration'''

    _data = None

    def __init__(self, xml):
        self._data = {}

        for child in xml:
            if child.tag == 'entry':
                self._data[child.attrib['name']] = child.text

            elif child.tag == 'container':
                self._data[child.attrib['name']] = ConfigSettings(child)

    def __getattr__(self, name):
        return self._data[name]

class ConfigSource(object):
    '''Source definitions

    Members:
    parent -- Parent of entry
    name -- Name of the source (referenced by targets)
    filename -- Source file
    '''

    def __init__(self, parent, xml):
        self.parent = parent
        self.name = xml.find('name').text
        self.filename = xml.find('filename').text

    @property
    def mtime(self):
        try:
            return os.stat(self.parent.locator.find(self.filename))[stat.ST_MTIME]

        except ResourceError:
            return 0

class ConfigTarget(object):
    '''Target definitions

    Members:
    parent -- Parent of entry
    name -- Name of the source (referenced by targets)
    filename -- Source file
    settings -- Target settings
    '''

    def __init__(self, parent, xml):
        self.parent = parent
        self.source = xml.find('source').text

        settings_xml = xml.find('settings')
        if settings_xml is not None:
            self.settings = ConfigSettings(settings_xml)

        else:
            self.settings = ConfigSettings(())

        self.generator = xml.find('generator').text
        self.module, self.gentype = self.generator.split(':', 1)

        self.target = xml.find('target').text

    @property
    def mtime(self):
        try:
            return os.stat(self.parent.write_locator.find(self.target))[stat.ST_MTIME]

        except ResourceError:
            return 0

class Config(object):
    '''Configuration object

    Members:
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

    _config_locator = None
    _write_locator = None
    _system_locator = None
    _locator = None

    _raw_xml = None
    _version = None

    _sources = None
    _targets = None
    _copy_list = None

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

    def __init__(self, data = None, filename = None, system_locator = None):
        self._sources = []
        self._targets = []
        self._copy_list = []

        self._config_locator = FileResourceLocator()
        self._write_locator = FileResourceLocator()
        self._system_locator = system_locator if system_locator is not None else FileResourceLocator()

        self._locator = FallbackLocator()
        self._locator.add_locator(self._write_locator)
        self._locator.add_locator(self._config_locator)
        self._locator.add_locator(self._system_locator)

        self._raw_xml = source.load(filename = filename, locator = self._system_locator).getroot()
        self._version = Version.load_from_string(self._raw_xml.get('version', '1.0'))

        if self._version > Config.CURRENT_VERSION:
            raise VersionMismatchError("Configuration is more recent than supported")

        if self._version <= Config.DEPRECATED_VERSION:
            raise VersionMismatchError("Configuration format deprecated")

        source.validate(self._raw_xml, filename = 'config.xsd', locator = ModuleLocator(__import__(__name__)))

        for entry in self._raw_xml:
            if entry.tag == 'paths':
                for path in entry:
                    if path.tag == 'target':
                        self._write_locator.add_path(path.text)

                    elif path.tag == 'path':
                        self._config_locator.add_path(path.text)

            elif entry.tag == 'source':
                self._sources.append(ConfigSource(self, entry))

            elif entry.tag == 'target':
                self._targets.append(ConfigTarget(self, entry))
