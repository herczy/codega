'''Build handling'''

import sys

import source
from config import Config
from generator import GeneratorBase
from rsclocator import FileResourceLocator, FallbackLocator, ModuleLocator

class Context(object):
    builder = None
    config = None
    target = None

    def __init__(self, builder, config, target):
        self.builder = builder
        self.config = config
        self.target = target

class Builder(object):
    '''Object used for building the target files'''

    def __init__(self, config_file):
        self._system_locator = FileResourceLocator('./')
        self._config = Config(filename = config_file, system_locator = self._system_locator)
        self._sources = {}

    def load_generator(self, module, clsname):
        mod = self._config.locator.import_module(module)
        cls = getattr(mod, clsname)

        if not issubclass(cls, GeneratorBase):
            print cls
            raise ImportError("%s:%s is not a generator" % (module, clsname))

        return cls

    def find_source(self, source_name):
        for source in self._config.sources:
            if source.name == source_name:
                return source

        raise KeyError("Source %s does not exist" % source.name)

    def find_target(self, target_file):
        for target in self._config.targets:
            if target.target == target_file:
                return target

        raise KeyError("Target %s does not exist" % target.target)

    def load_source(self, source_name):
        if not self._sources.has_key(source_name):
            src = self.find_source(source_name)
            self._sources[source_name] = source.load(filename = src.filename, locator = self._config.locator).getroot()

        return self._sources[source_name]

    def __build(self, target, force_rebuild):
        if not force_rebuild:
            source = self.find_source(target.source)
            if source.mtime <= target.mtime:
                return

        source = self.load_source(target.source)

        generator_class = self.load_generator(target.module, target.gentype)
        generator = generator_class()

        context = Context(self, self._config, target)

        generator.validate(source, context)
        generator.generate(source, open(target.target, 'w'), context)

    def build(self, target, force_rebuild = False):
        target = self.find_target(target)
        self.__build(target, force_rebuild = force_rebuild)

    def build_all(self, force_rebuild = False):
        for target in self._config.targets:
            self.__build(target, force_rebuild = force_rebuild)

    @staticmethod
    def main():
        import optparse

        parser = optparse.OptionParser(usage = '%prog <options>')
        parser.add_option('-c', '--config',  default = 'codega.xml',
                          help = 'Specify config file (default: %default)')
        parser.add_option('-t', '--target', default = [], action = 'append',
                          help = 'Specify targets (default: all)')
        parser.add_option('-f', '--force', default = False, action = 'store_true',
                          help = 'Force rebuild')
        parser.add_option('-d', '--debug', default = False, action = 'store_true',
                          help = 'Produce debug output')
        opts, args = parser.parse_args()

        try:
            builder = Builder(opts.config)
            if opts.target:
                map(lambda t: builder.build(t, force_rebuild = opts.force), opts.target)

            else:
                builder.build_all(force_rebuild = opts.force)

        except Exception, e:
            if opts.debug:
                raise

            print >>sys.stderr, "Error: %s" % e
