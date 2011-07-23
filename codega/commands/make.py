import sys
import optparse

from codega.rsclocator import FileResourceLocator
from codega.config import Config
from codega.generator import GeneratorBase
from codega.context import Context
from codega.error import ResourceError
from codega import logger

from base import OptparsedCommand

def build_target(config, target):
    generator = load_generator(config, target.module, target.gentype)
    context = Context(config, target.sourceref, target)
    destination = sys.stdout if target.target == 'sys.stdout' else config.locator.open_writable_resource(target.target)

    generator.validate(target.sourceref.data, context)
    destination.write(generator.generate(target.sourceref.data, context))
    destination.close()

def load_generator(config, module, clsname):
    mod = config.locator.import_module(module)
    gen = getattr(mod, clsname)

    if isinstance(gen, GeneratorBase):
        return gen

    if issubclass(gen, GeneratorBase):
        return gen()

    raise ImportError("%s:%s is not a generator class or instance" % (module, clsname))

class CommandMake(OptparsedCommand):
    _arg = None

    def __init__(self):
        options = [
            optparse.make_option('-c', '--config',  default = 'codega.xml',
                                 help = 'Specify config file (default: %default)'),
            optparse.make_option('-t', '--target', default = [], action = 'append',
                                 help = 'Specify targets (default: all)'),
            optparse.make_option('-f', '--force', default = False, action = 'store_true',
                                 help = 'Force rebuild'),
        ]

        super(CommandMake, self).__init__('make', options, helpstring = 'Build codega targets listed in the make file')

    def execute(self):
        # Load configuration file
        try:
            config = Config.load(self.opts.config)

        except ResourceError, rsc_error:
            print >>sys.stderr, 'Config file not found: %r' % rsc_error.resource
            return False

        if self.opts.force:
            build_list = list(config.targets)

        else:
            build_list = list(config.find_need_rebuild())

        for target in build_list:
            build_target(config, target)

        return True
