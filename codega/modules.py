'''Module handler classes

This module handles the generator- and filter module loading and also has the base classes
for these module types.

A module must have a __module_class__ attribute containing the generator- or filter class.
When loading, this will be instantiated.
'''
from lxml import etree

try:
    from StringIO import StringIO

except ImportError:
    from cStringIO import StringIO

from version import Version
from rsclocator import ModuleLocator

class Module(object):
    '''Codega module.

    A codega module contains specific information that can be used
    to extend the base framework.

    Members:
    _module -- Imported module
    _config -- Module configuration
    _info -- Module information
    '''

    _module = None
    _config = None
    _info = None

    def __init__(self, module, config):
        self._module = module
        self._config = config
        self._info = {}

        self._parse_info(**self._module.__info__)

    def _parse_info(self, **kwargs):
        '''Load module-related information'''

        self._info.update(kwargs)

    def set_config(self, config):
        '''Set configuration for module'''

        self._config = config

    @property
    def config(self):
        '''Configuration to use module with'''

        return self._locator

    @property
    def module(self):
        '''Imported module'''

        return self._module

    @property
    def info(self):
        '''Information getter property'''

        class _getter(object):
            def __getattr__(_, name):
                return self._info[name]

        return _getter()

class GeneratorModule(Module):
    '''Generator modules

    Generator modules take an XML tree and generate some output.

    Members:
    _generators -- Dictionary of generator classes
    _validator -- Source validator
    '''

    _generators = None
    _validator = None

    def _parse_info(self, generators, validator = None, **kwargs):
        '''Parse module info. A 'generators' key is necessary!'''

        self._generators = generators
        self._validator = validator

        super(GeneratorModule, self)._parse_info(**kwargs)

    def validate(self, xml):
        '''Validate the XML source tree.

        Arguments:
        xml -- The result of the XML parser (etree._Element)
        '''

        if self._validator is None:
            return True

        xsd_file = open(self._locator.find(self._validator))
        xsd = etree.XMLSchema(etree.parse(xsd_file))
        return xsd.validate(xml)

    def generate(self, source, gentype, target):
        '''Function for calling the appropriate generator

        Arguments:
        source -- Source XML tree
        gentype -- Generator type to use
        target -- Destination file descriptor
        context -- Additional builtin values
        '''

        if not self.validate(source):
            raise ValueError("Source XML invalid")

        self._generators[gentype]()(source, target)

class FilterModule(Module):
    '''Filter modules.

    Filter modules transform an XML or collect data from them for later use.

    Members:
    _filter -- Filter callable
    '''

    _filter = None

    def _parse_info(self, filter_callable, **kwargs):
        '''Parse module info. A 'filter' key is necessary!'''

        self._filter = filter_callable
        super(FilterModuleBase, self)._parse_info(**kwargs)

    def filter(self, source):
        '''Filter the source'''

        return self._filter(source)

def load_module(name, locator, config, modtype):
    '''Load a codega module

    Arguments:
    name -- Module name
    locator -- Module locator
    config -- Configuration
    modtype -- Module type class
    '''

    mod = locator.import_module(name)

    if not issubclass(mod.__info__['type'], modtype):
        raise ImportError("Module %s is of invalid type" % name)

    return mod.__info__['type'](mod, config)
