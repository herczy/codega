import os.path
import stat

from source import SourceBase
from rsclocator import FileResourceLocator, FallbackLocator
from generator import GeneratorBase
from context import Context
from error import StateError
from decorators import abstract

def get_module_time(locator, module):
    mod = locator.import_module(module)
    dirname, basename = os.path.split(mod.__file__)

    if os.path.splitext(basename)[0] != '__init__':
        return Builder.mtime(mod.__file__)

    res = []
    for root, dirs, files in os.walk(dirname):
        res.extend((Builder.mtime(os.path.join(root, f)) for f in files))

    return max(res)

class TaskBase(object):
    '''Task base for building
    
    Members:
    _builder -- The parent of the task
    '''

    _builder = None

    def __init__(self, builder):
        self._builder = builder

    @abstract
    def check_need_run(self):
        '''Check if the task needs to be run'''
        
    @abstract
    def execute(self):
        '''Execute the task'''
        
class BuildTask(TaskBase):
    '''Build a configuration target'''
    
    _config = None
    _locator = None
    _source = None
    _target = None
    
    _destination = None

    @staticmethod
    def mtime(filename):
        if os.path.exists(filename):
            return os.stat(filename)[stat.ST_MTIME]

        return 0
    
    def __init__(self, parent, config, locator, source, target):
        self._config = config
        self._locator = locator
        self._source = source
        self._target = target
        self._destination = os.path.join(self._locator.find(self._config.paths.destination), self._target.filename)
        
        super(BuildTask, self).__init__(parent)

    def check_need_run(self):
        # Check if we need to rebuild the target
        if not os.path.exists(self._destination):
            return True

        modules = [ 'codega', self._source.parser.module, self._target.generator.module ]
    
        # If the destination modification time is smaller than any other time (mtime
        # of any of the modules or files) we need to rebuild
        time = 0
        time = max(time, BuildTask.mtime(self._soruce.resource))
        time = reduce(max, [ get_module_time(self._locator, m) for m in modules ], time)

        return Builder.mtime(self._destination) < time

    def execute(self):
        # Generation context
        context = Context(self._config, self._source, self._target)

        # Load source
        data = self._builder.cache(self._source.name, lambda key: self.get_source(self._source))

        # Generate output
        generator = self._target.generator.load(self._locator)
        if not issubclass(generator, GeneratorBase):
            raise StateError("Generator reference %s could not be loaded" % generator)
        output = generator.run(data, context)

        # Write output
        destination = open(self._destination, 'w')
        destination.write(output)
        destination.close()
        
    def get_source(self, source):
        parser = self._source.parser.load(self._locator)
        if not issubclass(parser, SourceBase):
            raise StateError("Parser reference %s could not be loaded" % parser)
        return parser().load(self._source.resource).getroot()
    
class Builder(object):
    '''Base object for builders

    Members:
    _cache -- Object cache (mostly for sources)
    _tasks -- Task backlog
    _locator -- Basic resource locator
    '''
    
    _cache = None
    _tasks = None
    _locator = None

    def __init__(self, locator):
        self._cache = {}
        self._tasks = []
        self._locator = locator

    def cache(self, key, calc):
        '''Get or calculate resource'''

        if not self._cache.has_key(key):
            self._cache[key] = calc(key)

        return self._cache[key]

    def push_task(self, task):
        self._tasks.append(task)
        
    def build(self, force = False):
        while self._tasks:
            task = self._tasks.pop()

            if not force and not task.check_need_run():
                continue 

            task.execute()

        self._tasks = []

class ConfigBuilder(Builder):
    '''Build targets from a config'''

    def __init__(self, config, base_locator):
        self._config = config

        # Make locator
        locator = FallbackLocator()
        for path in config.paths.paths:
            locator.add_locator(FileResourceLocator(base_locator.find(path)))
            
        super(ConfigBuilder, self).__init__(locator)
    
    def add_target(self, target):
        '''Add a configuration target'''
        
        config = target.parent
        source = config.sources[target.source]
        #import pdb; pdb.set_trace()
        task = BuildTask(self, config, self._locator, source, target)
        
        self.push_task(task)
