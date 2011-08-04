'''Locator objects

A locators purposes are the following:
 * locate a file
 * list the reachable resources
 * import modules
 * open a resource for writing
'''
import os, os.path
import sys

from error import ResourceError
from decorators import abstract

class ResourceLocatorBase(object):
    '''Resource loader base object'''

    def __init__(self):
        pass

    @abstract
    def find(self, resource):
        '''Abstract method for locating a resource'''

    @abstract
    def list_resources(self):
        '''List resources reachable with locator'''

    @abstract
    def import_module(self, module):
        '''Abstract method for locating a module'''

class FileResourceLocator(ResourceLocatorBase):
    '''Class that helps locating files from the given path.

    In this case the locator tries to locate a path relative to the one set.

    Members:
    _paths -- List of paths to scan
    '''

    _path = None

    def __init__(self, path):
        super(ResourceLocatorBase, self).__init__()

        self._path = path

    def import_module(self, modname):
        '''Imports a module. This function extends the system path list temporarly to do this.

        Arguments:
        modname -- Module name, Python style
        '''

        oldpath = list(sys.path)
        try:
            sys.path.insert(0, self._path)
            __import__(modname)
            return sys.modules[modname]

        finally:
            sys.path = oldpath

    def find(self, resource):
        '''Find a resource in the given path.

        Arguments:
        resource -- Relative resource path
        '''

        dest = os.path.join(self._path, resource)

        if not os.path.exists(dest):
            raise ResourceError("Resource could not be located", resource = resource)

        return dest

    def list_resources(self):
        '''List file resources reachable from the given path'''

        abspath = os.path.abspath(self._path)
        for dirpath, dirnames, filenames in os.walk(abspath):
            relpath = dirpath[len(abspath) + 1:]

            for fn in filenames:
                yield os.path.join(relpath, fn)

class FallbackLocator(ResourceLocatorBase):
    '''Locator object containing a list of other locators.

    This locator iterates its entries and tries to find the resource with its entries. Used for combining
    different ResourceLocatorBase instances instead of creating a big locator.

    Members:
    _locators -- List of locators
    '''

    _locators = None

    def __init__(self, locators = []):
        super(FallbackLocator, self).__init__()

        self._locators = list(locators)

    def add_locator(self, locator, index = None):
        if index is None:
            self._locators.append(locator)

        else:
            self._locators.insert(index, locator)

    def find(self, resource):
        for locator in self._locators:
            try:
                return locator.find(resource)

            except ResourceError:
                pass

        raise ResourceError("Resource could not be located", resource = resource)

    def list_resources(self):
        hasbeen = set()
        for locator in self._locators:
            for rsc in locator.list_resources():
                if rsc in hasbeen:
                    continue

                hasbeen.add(rsc)
                yield rsc

    def import_module(self, module):
        for locator in self._locators:
            try:
                return locator.import_module(module)

            except ImportError, e:
                if str(e) != "No module named %s" % module:
                    raise

                pass

        raise ImportError("No module named %s" % module)

class ModuleLocator(FileResourceLocator):
    '''Locate files relative to module path'''

    def __init__(self, module):
        path = os.path.dirname(module.__file__)
        super(ModuleLocator, self).__init__(path)
