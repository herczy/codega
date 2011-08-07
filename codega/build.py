import os.path
import stat

from source import SourceBase
from rsclocator import FileResourceLocator, FallbackLocator
from generator import GeneratorBase
from context import Context
from error import StateError

class Builder(object):
    '''Build the given targets.

    Members:
    _base_locator -- Basic resource locator
    _parsed -- Parsed source results
    '''

    _base_locator = None
    _parsed = None

    def __init__(self, locator):
        self._base_locator = locator
        self._parsed = {}

    @staticmethod
    def mtime(filename):
        if os.path.exists(filename):
            return os.stat(filename)[stat.ST_MTIME]

        return 0

    def get_module_time(self, locator, module):
        mod = locator.import_module(module)
        dirname, basename = os.path.split(mod.__file__)

        if os.path.splitext(basename)[0] != '__init__':
            return Builder.mtime(mod.__file__)

        res = []
        for root, dirs, files in os.walk(dirname):
            res.extend((Builder.mtime(os.path.join(root, f)) for f in files))

        return max(res)

    def need_rebuild(self, locator, etalon, files, modules):
        # No etalon means a rebuild is necessary
        if not os.path.exists(etalon):
            return True

        # If the destination modification time is smaller than any other time (mtime
        # of any of the modules or files) we need to rebuild
        times = []
        times.extend([ Builder.mtime(locator.find(f)) for f in files ])
        times.extend([ self.get_module_time(locator, m) for m in modules ])

        return Builder.mtime(etalon) < max(times)

    def build(self, config, target, force = False):
        # Make locator
        locator = FallbackLocator()
        for path in config.paths.paths:
            locator.add_locator(FileResourceLocator(self._base_locator.find(path)))

        # Check if we need to rebuild the target
        destination = os.path.join(self._base_locator.find(config.paths.destination), target.filename)
        source = config.sources[target.source]

        if not force:
            files = [ source.filename ]
            modules = [ 'codega', source.parser.module, target.generator.module ]

            if not self.need_rebuild(locator, destination, files, modules):
                return

        # Generation context
        context = Context(config, source, target)

        # Load source
        if not self._parsed.has_key(source.name):
            parser = source.parser.load(locator)
            if not issubclass(parser, SourceBase):
                raise StateError("Parser reference %s could not be loaded" % parser)
            self._parsed[source.name] = parser().load(source.resource).getroot()

        data = self._parsed[source.name]

        # Generate output
        generator = target.generator.load(locator)
        if not issubclass(generator, GeneratorBase):
            raise StateError("Generator reference %s could not be loaded" % generator)
        output = generator.run(data, context)

        # Write output
        destination = open(destination, 'w')
        destination.write(output)
        destination.close()

    def build_list(self, config, target_list, force = False):
        map(lambda t: self.build(config, t, force = force), target_list)
