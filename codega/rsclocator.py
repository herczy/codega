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

class ResourceLocatorBase(object):
    '''Resource loader base object'''

    def __init__(self):
        pass

    def find(self, resource):
        '''Abstract method for locating a resource'''

        raise NotImplementedError("ResourceLocatorBase.find is abstract")

    def list_resources(self):
        '''List resources reachable with locator'''

        raise NotImplementedError("ResourceLocatorBase.list_resources is abstract")

    def import_module(self, module):
        '''Abstract method for locating a module'''

        raise NotImplementedError("ResourceLocatorBase.import_module is abstract")

    def open_writable_resource(self, name):
        '''Open a resource for writing.'''

        raise NotImplementedError("ResourceLocatorBase.open_writable_resource is abspath")

class FileResourceLocator(ResourceLocatorBase):
    '''Class that helps locating files from the given paths.

    Works in a similar fassion to sys.path except its not limited to Python modules. Note
    that the first path is used as the destination directory for open_writable_resource

    Members:
    _paths -- List of paths to scan
    '''

    _paths = None

    def __init__(self, paths = []):
        super(ResourceLocatorBase, self).__init__()

        self._paths = list(paths)

    def add_path(self, path, index = None):
        if index is None:
            self._paths.append(path)

        else:
            self._paths.insert(index, path)

    def import_module(self, modname):
        '''Imports a module from the given path list.

        Arguments:
        modname -- Module name, Python style
        '''

        oldpath = sys.path
        try:
            sys.path = list(self._paths)
            sys.path.extend(oldpath)
            return __import__(modname)

        finally:
            sys.path = oldpath

    def find(self, resource):
        '''Find a resource in the given path list.

        Arguments:
        resource -- Relative resource path
        '''

        for path in self._paths:
            dest = os.path.join(path, resource)

            if os.path.isfile(dest):
                return dest

        raise ResourceError("Resource could not be located", resource = resource)

    def list_resources(self):
        '''List file resources reachable from given paths'''

        for path in self._paths:
            abspath = os.path.abspath(path)
            for dirpath, dirnames, filenames in os.walk(abspath):
                relpath = dirpath[len(abspath) + 1:]

                for fn in filenames:
                    yield os.path.join(relpath, fn)

    def open_writable_resource(self, name):
        '''Write data to the first path in list'''

        write_path = self._paths[0]
        full_filename = os.path.join(write_path, name)
        return open(full_filename, 'w')

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
                if str(e) != "ImportError: No module named dumper":
                    raise

                pass

        raise ImportError("No module named %s" % module)

    def open_writable_resource(self, name):
        return self._locators[0].open_writable_resource(name, data)

class ModuleLocator(FileResourceLocator):
    '''Locate files relative to module path'''

    def __init__(self, module):
        path = os.path.dirname(module.__file__)
        super(ModuleLocator, self).__init__([ path ])
