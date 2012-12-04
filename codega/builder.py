import os
import stat
import shutil
import re

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


def environment_replacement(string):
    def __replace(match):
        logger.debug('Match found: %s' % match.group())
        name = match.group()[1:-1]
        return os.getenv(name)

    return re.sub(r'\@[a-zA-Z_][a-zA-Z0-9_]*\@', __replace, string)


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
            modules = ['codega', source.parser.module, self.__target.generator.module]

            # If the destination modification time is more recent than any other
            # listed modification time (mtime of any of the modules or files) we
            # need to rebuild
            time = 0
            time = max(time, get_mtime(source.resource))
            time = reduce(max, [get_module_time(self.parent.locator, m) for m in modules], time)

            if get_mtime(destination) >= time:
                return

        # Generation context
        context = Context(self.parent.config, source, self.__target)

        # Load source
        data = self.parent.get_source(source)

        # Generate output
        generator = self.__target.generator.load(self.parent.locator)
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

    def __str__(self):
        return 'target(%s)' % self.__target.filename


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


class BuildRunner(object):
    def __init__(self, config, base_path='.'):
        self.__config = config
        self.__base_path = base_path
        self.__locator = build_locator(config, base_path=base_path)

        self.__source_results = {}

        self.__builders = []
        self.__init_builders()

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
            config = ConfigSource(BuildRunner.__environment_replacements).load(config_path)

        except ParseError, parse_error:
            logger.error('Parse error: %s', parse_error)
            logger.exception()
            return False

        return cls(config, base_path=os.path.dirname(config_path)).run_task(task, **kwargs)

    @property
    def config(self):
        return self.__config

    @property
    def locator(self):
        return self.__locator

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

    def get_source(self, source):
        if isinstance(source, basestring):
            source = self.__config.sources[source]

        logger.debug('Trying to parse source %r' % source.name)
        if source not in self.__source_results:
            parser = source.parser.load(self.__locator)
            if isinstance(parser, type) and issubclass(parser, SourceBase):
                parser = parser()

            if not isinstance(parser, SourceBase):
                raise BuilderError("Parser reference %s could not be loaded" % parser)

            res = parser.load(source.resource, self.__locator)
            if isinstance(res, etree._ElementTree):
                res = res.getroot()

            for transform in source.transform:
                modtrans = transform.load(self.__locator)
                res = modtrans(res)

            self.__source_results[source] = res
            logger.info('Source %r successfuly parsed' % source.name)

        else:
            logger.debug('Source already parsed')

        return self.__source_results[source]

    def __run_external(self, task, **kwargs):
        for ext in self.__config.external:
            if not self.__class__.run_task_file(self.__locator.find(ext), task, **kwargs):
                raise BuilderError('Could not run task %r on external %s' % (task, ext))

    def __init_builders(self):
        # Add targets
        for name, target in self.__config.targets.items():
            self.__builders.append(TargetBuilder(self, target))

        # Add copies
        for name, copy in self.__config.copy.values():
            self.__builders.append(CopyBuilder(self, copy))

        # Add externals
        for ext in self.__config.external:
            self.__builders.append(ExternalBuilder(self, ext))

    @staticmethod
    def __environment_replacements(text):
        def __replace(match):
            logger.debug('Match found: %s' % match.group())
            name = match.group()[1:-1]
            return os.getenv(name)

        return re.sub(r'\@[a-zA-Z_][a-zA-Z0-9_]*\@', __replace, text)
