import os
import stat
import shutil

from lxml import etree

from codega import logger
from codega.rsclocator import FallbackLocator, FileResourceLocator
from codega.source import SourceBase
from codega.context import Context
from codega.decorators import abstract, mark, has_mark
from codega.generator.base import GeneratorBase
from codega.config.source import ConfigSource, ParseError


class BuilderError(Exception):
    '''The builder encountered an error'''


def get_mtime(filename):
    '''Get the modification time of a file'''

    if os.path.exists(filename):
        return os.stat(filename)[stat.ST_MTIME]

    return 0


def get_module_time(locator, module):
    '''Get the modification time for a module'''

    mod = locator.import_module(module)
    dirname, basename = os.path.split(mod.__file__)

    if os.path.splitext(basename)[0] != '__init__':
        return get_mtime(mod.__file__)

    res = []
    for root, _, files in os.walk(dirname):
        res.extend((get_mtime(os.path.join(root, f)) for f in files))

    return max(res)


def build_locator(config, base_path=None):
    if base_path is None:
        base_path = '.'

    locator = FallbackLocator()
    for path in config.paths.paths:
        locator.add_locator(FileResourceLocator(os.path.join(base_path, path)))
    locator.add_locator(FileResourceLocator(base_path))

    return locator


def get_config(config_file):
    if config_file is None:
        if os.path.isfile('codega.xml'):
            return 'codega.xml'

    elif os.path.isfile(config_file):
        return config_file


def task(name):
    return mark('task', True)


class BuilderBase(object):
    def __init__(self, parent):
        self.__parent = parent

    @property
    def parent(self):
        return self.__parent

    def check_filter(self, filter, name):
        return filter is None or filter(name)

    def run_task(self, task, *args, **kwargs):
        if hasattr(self, task):
            fun = getattr(self, task)

            if has_mark(fun, 'task'):
                fun(*args, **kwargs)
                return True

        return False

    def __str__(self):
        return 'builder:%d' % id(self)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self)


class TargetBuilder(BuilderBase):
    def __init__(self, parent, target):
        super(TargetBuilder, self).__init__(parent)

        self.__target = target

    @task('build')
    def build(self, filter=None, force=False):
        if not self.check_filter(filter, self.__target.filename):
            return

        destination = self.parent.get_target_path(self.__target.filename)
        source = self.parent.config.sources[self.__target.source]

        # Check if we need to rebuild the target
        if not force and os.path.exists(destination):
            modules = [ 'codega', source.parser.module, self.__target.generator.module ]

            # If the destination modification time is more recent than any other
            # listed modification time (mtime of any of the modules or files) we
            # need to rebuild
            time = 0
            time = max(time, get_mtime(source.resource))
            time = reduce(max, [ get_module_time(self.parent.locator, m) for m in modules ], time)

            if get_mtime(destination) >= time:
                return

        # Generation context
        context = Context(self.parent.config, source, self.__target)

        # Load source
        data = self.parse_source(source)

        # Generate output
        generator = self.get_generator(self.__target)
        if isinstance(generator, type) and issubclass(generator, GeneratorBase):
            generator = generator()

        elif not isinstance(generator, GeneratorBase):
            raise BuilderError("Generator reference %s could not be loaded" % generator)

        output = generator.generate(data, context)

        # Write output
        with open(destination, 'w') as out:
            out.write(output)

    @task('cleanup')
    def cleanup(self, filter=None):
        if not self.check_filter(filter, self.__target.filename):
            return

        self.parent.remove_dest_file(self.__target.filename)

    def parse_source(self, source):
        if isinstance(source, basestring):
            source = self.__config.sources[source]

        logger.debug('Trying to parse source %r' % source.name)
        if not self.parent.is_cached(source):
            logger.info('Source %r successfuly parsed' % source.name)

        else:
            logger.debug('Source already parsed')

        return self.parent.get_cached(source, self.__parse_source_noncached, source)

    def get_generator(self, target):
        return target.generator.load(self.parent.locator)

    def get_parser(self, source):
        return source.parser.load(self.parent.locator)

    def __str__(self):
        return 'target(%s)' % self.__target.filename

    def __parse_source_noncached(self, source):
        parser = self.get_parser(source)
        if not issubclass(parser, SourceBase):
            raise BuilderError("Parser reference %s could not be loaded" % parser)

        res = parser().load(source.resource, self.parent.locator)
        if isinstance(res, etree._ElementTree):
            res = res.getroot()

        for transform in source.transform:
            modtrans = transform.load(self.parent.locator)
            res = modtrans(res)

        return res

class CopyBuilder(BuilderBase):
    def __init__(self, parent, copy):
        super(CopyBuilder, self).__init__(parent)

        self.__copy = copy

    @task('build')
    def build(self, filter=None, force=False):
        if not self.check_filter(filter, self.__copy.target):
            return

        source = self.parent.locator.find(self.__copy.source)
        destination = self.parent.get_target_path(self.__copy.target)

        if get_mtime(source) < get_mtime(destination):
            return

        shutil.copy(source, destination)

    @task('cleanup')
    def cleanup(self, filter=None):
        if not self.check_filter(filter, self.__copy.target):
            return

        self.parent.remove_dest_file(self.__copy.target)

    def __str__(self):
        return 'copy(%s)' % self.__copy.target


class ExternalBuilder(BuilderBase):
    def __init__(self, parent, external):
        super(ExternalBuilder, self).__init__(parent)

        self.__external = external

    def run_task(self, task, *args, **kwargs):
        if not BuildRunner.run_task_file(self.parent.locator.find(self.__external), task, *args, **kwargs):
            raise BuilderError('Could not run task %r on external %s' % (task, self.__external))

        return True

    def __str__(self):
        return 'external(%s)' % self.__external


class ModuleTarget(TargetBuilder):
    def __init__(self, parent, target, module):
        super(TargetBuilder, self).__init__(parent, target)

        self.__module = module

    def get_generator(self, target):
        return self.__module.get_generator(target)

    def get_parser(self, source):
        return self.__module.get_parser(source)


class ModuleBuilder(BuilderBase):
    def __init__(self, parent, module):
        super(ModuleBuilder, self).__init__(parent)

        self.__module_config = module
        py_module = self.__module_config.reference.load(parent.locator)
        self.__module = getattr(py_module, 'Module')(self.parent.locator, module)

        target_constructor = lambda parent, target: ModuleTarget(parent, target, self.__module)
        self.__builder_class = type('ModuleBuildRunner', (BuildRunner,), dict(target_class=target_constructor))

    def run_task(self, task, *args, **kwargs):
        return self.__builder_class(self.__module.get_config(), self.parent.base_path).run_task()

    def __str__(self):
        return 'module(%s)' % self.__module_config.name


class BuildRunner(object):
    target_class = TargetBuilder
    copy_class = CopyBuilder
    external_class = ExternalBuilder
    module_class = ModuleBuilder

    def __init__(self, config, base_path='.'):
        self.__config = config
        self.__base_path = base_path
        self.__locator = build_locator(config, base_path=base_path)

        self.__source_results = {}
        self.__cache = {}

        self.__builders = []
        self.__init_builders()

    @property
    def config(self):
        return self.__config

    @property
    def locator(self):
        return self.__locator

    @property
    def base_path(self):
        return self.__base_path

    def is_cached(self, key):
        return key in self.__cache

    def get_cached(self, key, func, *args, **kwargs):
        if key not in self.__cache:
            self.__cache[key] = func(*args, **kwargs)

        return self.__cache[key]

    def run_task(self, task, *args, **kwargs):
        if not self.__builders:
            logger.error("No builders found")
            return False

        for builder in self.__builders:
            try:
                if not builder.run_task(task, *args, **kwargs):
                    logger.info('Builder has no task %s' % task)

                else:
                    logger.info('Completed task %s on %s' % (task, builder))

            except Exception, error:
                logger.critical('Could not complete %s: %s', task, error)
                logger.exception()
                return False

        return True

    @classmethod
    def run_task_file(cls, config_file, task, **kwargs):
        config_path = get_config(config_file)

        # Check if file exists
        if config_path is None:
            if config_file:
                logger.critical("File %r not found", config_file)

            else:
                logger.critical("No suitable config file could be found")

            return False

        # Load configuration file
        try:
            logger.info('Loading config file %r', config_path)
            config = ConfigSource().load(config_path)

        except ParseError, parse_error:
            logger.error('Parse error: %s', parse_error)
            logger.exception()
            return False

        return cls(config, base_path=os.path.dirname(config_path)).run_task(task, **kwargs)

    def get_target_path(self, relpath):
        abspath = os.path.join(self.__base_path, self.__config.paths.destination, relpath)
        dirname = os.path.dirname(abspath)
        if not os.path.isdir(dirname):
            raise BuilderError('%r should be a directory' % dirname)

        return abspath

    def remove_dest_file(self, relpath):
        logger.debug('Trying to remove %r' % relpath)
        try:
            destination = self.get_target_path(relpath)

        except BuilderError:
            logger.debug('Path containing %r not found' % relpath)
            return

        if os.path.isfile(destination):
            logger.info('Removing file %s' % destination)
            os.unlink(destination)

        else:
            logger.debug('File %r not found' % relpath)

    def __init_builders(self):
        self.__add_items(self.__config.targets.values(), self.target_class)
        self.__add_items(self.__config.copy.values(), self.copy_class)
        self.__add_items(self.__config.external, self.external_class)
        self.__add_items(self.__config.modules.values(), self.modules_class)

    def __add_items(self, items, cls):
        for item in items:
            self.__builders.append(cls(self, item))
