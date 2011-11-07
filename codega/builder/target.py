'''
Build tasks handle the building of a target.
'''

import os.path
import stat

from codega.generator.base import GeneratorBase
from codega.context import Context
from codega.source import SourceBase
from codega.error import StateError

from base import TaskBase, job
from time import get_module_time, get_mtime

class TargetTask(TaskBase):
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

        super(TargetTask, self).__init__(builder)

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
        if isinstance(generator, type) and issubclass(generator, GeneratorBase):
            generator = generator()

        elif not isinstance(generator, GeneratorBase):
            raise StateError("Generator reference %s could not be loaded" % generator)

        output = generator.generate(data, context)

        # Write output
        destination = open(self._destination, 'w')
        destination.write(output)
        destination.close()

    @job('cleanup')
    def job_cleanup(self, job_id, force):
        if os.path.isfile(self._destination):
            os.remove(self._destination)

