from lxml import etree

try:
    from StringIO import StringIO

except ImportError:
    from cStringIO import StringIO

from version import Version
from rsclocator import ModuleLocator

class ModuleBase(object):
    '''Base class for different module types

    Members:
    _name -- Module name
    _version -- Module version
    _locator -- Module locator
    _info -- Module information (a dict)
    '''

    _name = None
    _version = None
    _locator = None
    _info = None

    def __init__(self, name, version = Version(0), info = {}):
        self._name = name
        self._version = version
        self._info = info

    def set_locator(self, locator):
        self._locator = locator

    @property
    def info(self):
        class _getter(object):
            def __getattr__(_, name):
                return self._info[name]

        return _getter()

class GeneratorModuleBase(ModuleBase):
    '''Base class for generator modules

    Members:
    _generators -- Dictionary of generator classes
    _validator -- Source validator
    '''

    _generators = None
    _validator = None

    def __init__(self, name, generators, validator = None, **kwargs):
        super(GeneratorModuleBase, self).__init__(name, **kwargs)

        self._generators = generators
        self._validator = validator

    def validate(self, xml):
        '''Validate the XML source tree.

        Arguments:
        xml -- The result of the XML parser (etree._Element)
        '''

        if self._validator is None:
            return True

        xsd_file = open(self._locator.find(self._validator))
        xsd = lxml.etree.XMLSchema(lxml.etree.parse(xsd_file))
        return xsd.validate(xml)

    def generate(self, source, gentype, target):
        '''Function for calling the appropriate generator

        Arguments:
        source -- Source XML tree
        gentype -- Generator type to use
        target -- Destination file descriptor
        '''

        if not self.validate(source):
            raise ValueError("Source XML invalid")

        obj = self._generators[gentype]()
        obj(source, target)

class FilterModuleBase(ModuleBase):
    '''Base class for filter modules

    Members:
    _filter -- Filter callable
    '''

    _filter = None

    def __init__(self, name, filter_callable, **kwargs):
        super(GeneratorModuleBase, self).__init__(name, **kwargs)

        self._filter = filter_callable

    def filter(self, source):
        '''Filter the source'''

        return self._filter(source)

def load_module(locator, name):
    mod = locator.load_module(name)

    if not hasattr(mod, '__module_class__'):
        raise ImportError("Module %s has no __module_class__" % name)

    return mod.__module_class__()

def load_generator(locator, name):
    obj = load_module(locator, name)

    if not isinstance(obj, GeneratorModuleBase):
        raise ImportError("Module %s is not a generator module" % name)

    return obj

def load_filter(locator, name):
    obj = load_module(locator, name)

    if not isinstance(obj, FilterModuleBase):
        raise ImportError("Module %s is not a filter module" % name)

    return obj
