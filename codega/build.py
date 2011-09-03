import os.path
import stat

from source import SourceBase
from rsclocator import FileResourceLocator, FallbackLocator
from generator import GeneratorBase
from context import Context
from error import StateError, ResourceError, ParseError
from config import save_config, parse_config_file, Config, Source, Target
from decorators import abstract, mark, collect_marked_bound
from version import Version
import logger
from codega.error import BuildError

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
    for root, dirs, files in os.walk(dirname):
        res.extend((get_mtime(os.path.join(root, f)) for f in files))

    return max(res)

def job(job_id, depends = ()):
    '''Marks a function as a preparator for the given task'''

    return mark('task_job', (job_id, depends))

class TaskBase(object):
    '''Task base for building

    Members:
    _builder -- The parent of the task
    '''

    _builder = None

    def __init__(self, builder):
        self._builder = builder

    def list_supported_jobs(self):
        '''List the supported job ID's of the task'''

        res = set()
        for (job_id, depends), job in collect_marked_bound(self, 'task_job'):
            res.add(job_id)

        return tuple(res)

    def build(self, job_id, force = False, skip = None):
        '''Execute a job in the task'''

        # The skip list is a list of jobs that have been done in
        # this iteration so they don't need to be redone
        if skip is None:
            skip = []

        # Find the handler for the job
        handler = None
        dependencies = None
        for (_job_id, depends), job in collect_marked_bound(self, 'task_job'):
            if _job_id == job_id:
                if handler is not None:
                    raise StateError("More than one handlers for the job %s in %s" % (mark, self.__class__.__name__))

                handler = job
                dependencies = depends

        # No job by the given ID
        if handler is None:
            return

        # Watch out for circular references
        skip.append(job_id)

        # Build dependencies, watch for recursion
        for dep in dependencies:
            if dep in skip:
                logger.warning('Dependency %s already built' % dep)
                continue

            self.build(dep, force = force, skip = skip)

        handler(job_id, force)

class BuildTask(TaskBase):
    '''Build a configuration target'''

    _config = None
    _locator = None
    _source = None
    _target = None
    _cache = None

    _destination = None

    def __init__(self, builder, config, locator, source, target, cache):
        self._config = config
        self._locator = locator
        self._source = source
        self._target = target
        self._destination = os.path.join(self._locator.find(self._config.paths.destination), self._target.filename)
        self._cache = cache

        super(BuildTask, self).__init__(builder)

    def get_source(self, source):
        parser = self._source.parser.load(self._locator)
        if not issubclass(parser, SourceBase):
            raise StateError("Parser reference %s could not be loaded" % parser)
        return parser().load(self._source.resource, self._locator).getroot()

    @job('parse')
    def job_parse(self, job_id, force):
        key = self._source.name
        if force or not self._cache.has_key(key):
            self._cache[key] = self.get_source(self._source)

        return self._cache[key]

    @job('build', depends = ('parse',))
    def job_build(self, job_id, force):
        # Check if we need to rebuild the target
        if not force and os.path.exists(self._destination):
            modules = [ 'codega', self._source.parser.module, self._target.generator.module ]

            # If the destination modification time is more recent than any other
            # listed modification time (mtime of any of the modules or files) we
            # need to rebuild
            time = 0
            time = max(time, get_mtime(self._source.resource))
            time = reduce(max, [ get_module_time(self._locator, m) for m in modules ], time)

            if get_mtime(self._destination) >= time:
                return

        # Generation context
        context = Context(self._config, self._source, self._target)

        # Load source
        data = self._cache[self._source.name]

        # Generate output
        generator = self._target.generator.load(self._locator)
        if not issubclass(generator, GeneratorBase):
            raise StateError("Generator reference %s could not be loaded" % generator)
        output = generator.run(data, context)

        # Write output
        destination = open(self._destination, 'w')
        destination.write(output)
        destination.close()

    @job('cleanup')
    def job_cleanup(self, job_id, force):
        if os.path.isfile(self._destination):
            os.remove(self._destination)

class Builder(object):
    '''Base object for builders

    Members:
    _cache -- Source cache for parse results
    _tasks -- Task backlog
    '''

    _cache = None
    _tasks = None

    def __init__(self):
        self._cache = {}
        self._tasks = []

    def push_task(self, task):
        '''Add a task to the task list'''

        self._tasks.append(task)

    def build(self, job_id, force = False):
        '''Build tasks.

        Note that the tasks will be removed!
        '''

        try:
            for task in self._tasks:
                logger.debug('Running job %s on task %s' % (job_id, task))
                task.build(job_id, force = force)

        except Exception, e:
            raise BuildError('Error detected during build: %s' % e)

class ProxyTask(TaskBase):
    '''Wrap function as a task'''

    def __init__(self, builder, build_function):
        self._build_function = build_function

        super(ProxyTask, self).__init__(builder)

    def build(self, job_id, force = False, skip = None):
        self._build_function(job_id = job_id, force = force)

class ConfigBuilder(Builder):
    '''Build targets from a config
    
    Members:
    _config -- Configuration for builder
    _locator -- Base locator for builder
    '''

    _config = None
    _locator = None

    def __init__(self, config, base_locator):
        self._config = config

        # Make locator
        self._locator = FallbackLocator()
        for path in config.paths.paths:
            self._locator.add_locator(FileResourceLocator(base_locator.find(path)))

        super(ConfigBuilder, self).__init__()

    def add_target(self, target):
        '''Add a configuration target'''

        config = target.parent
        source = config.sources[target.source]
        task = BuildTask(self, config, self._locator, source, target, self._cache)

        self.push_task(task)

    def add_external(self, external, targets = (), force = False):
        task = ProxyTask(self, lambda job_id, force: ConfigBuilder.run_make(job_id, external, targets = targets, force = force))
        self.push_task(task)

    @staticmethod
    def run_make(job_id, config_file, targets = (), force = False):
        #import pdb; pdb.set_trace()
        # Check if file exists
        if not os.path.isfile(config_file):
            logger.critical("File %r not found", config_file)
            return False

        # Locator from the config file
        base_locator = FileResourceLocator(os.path.dirname(config_file))

        # Load configuration file
        try:
            logger.info('Loading config file %r', config_file)
            config = parse_config_file(config_file)

        except ParseError, parse_error:
            logger.error('Parse error (at line %s): %s' % (parse_error.lineno, parse_error.message))
            return False

        # Populate list of build targets
        if targets:
            build_list = [config.targets[t] for t in targets]

        else:
            build_list = config.targets.values()

        # Populate external dependency list
        externals = list(config.external)

        # Populate config builder
        config_builder = ConfigBuilder(config, base_locator)

        # ... with externals
        for external in externals:
            config_builder.add_external(external, targets = targets, force = force)

        # ... and with targets
        for target in build_list:
            logger.debug('Adding target %s' % target.filename)
            config_builder.add_target(target)

        # Run build for targets
        config_builder.build(job_id, force = force)
        return True

    @staticmethod
    def run_build(job_id, source, parser, target, generator, includes = (), config_dest = None):
        if not source:
            logger.critical('Missing source')
            return False

        if not generator:
            logger.critical('Missing generator')
            return False

        config = Config()

        # Create source object
        source_obj = Source(config)
        source_obj.name = 'source'
        source_obj.resource = source
        if parser:
            source_obj.parser.load_from_string(parser)
        config.sources[source_obj.name] = source_obj

        # Create target object
        target_obj = Target(config)
        target_obj.source = 'source'
        target_obj.filename = target
        target_obj.generator.load_from_string(generator)
        config.targets[target_obj.filename] = target_obj

        # Create include list
        config.paths.destination = '.'
        for inc in includes:
            if not os.path.isdir(inc):
                logger.critical('Invalid path %r' % inc)
                return False
            config.paths.paths.append(inc)
        config.version = Version(1, 0)

        # Save config if requested
        if config_dest is not None:
            conf_xml = save_config(config)

            if config_dest:
                conf_file = open(config_dest, 'w')
                conf_file.write(conf_xml)
                conf_file.close()

        config_builder = ConfigBuilder(config, FileResourceLocator('.'))
        config_builder.add_target(target_obj)
        config_builder.build(job_id, force = True)
        return True
