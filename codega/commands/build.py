import os
import os.path
import sys
import optparse

from codega.config import *
from codega.build import Builder
from codega.rsclocator import FileResourceLocator
from codega import logger

from base import OptparsedCommand

class CommandBuild(OptparsedCommand):
    def __init__(self):
        options = [
            optparse.make_option('-s', '--source', default = None,
                                 help = 'Specify the source file'),
            optparse.make_option('-p', '--parser', default = 'codega.source:XmlSource',
                                 help = 'Specify the parser in <module>:<source class> format (default: %default)'),
            optparse.make_option('-t', '--target', default = 'codega.out',
                                 help = 'Specify the target file (default: %default)'),
            optparse.make_option('-g', '--generator', default = None,
                                 help = 'Specify the generator in <module>:<source class> format'),

            optparse.make_option('-I', '--include', default = ['.'], action = 'append',
                                 help = 'Add a new search path (for modules, sources, etc.)'),

            optparse.make_option('-c', '--config', default = None,
                                 help = 'Write the equivalent config to the given file'),
        ]

        super(CommandBuild, self).__init__('build', options, helpstring = 'Build the source with specified generator')

    def execute(self):
        if not self.opts.source:
            logger.critical('Missing source')
            return False

        if not self.opts.generator:
            logger.critical('Missing generator')
            return False

        config = Config()

        # Create source object
        source = Source(config)
        source.name = 'source'
        source.filename = self.opts.source
        if self.opts.parser:
            source.parser.load_from_string(self.opts.parser)
        config.sources[source.name] = source

        # Create target object
        target = Target(config)
        target.source = 'source'
        target.filename = self.opts.target
        target.generator.load_from_string(self.opts.generator)
        config.targets[target.filename] = target

        config.paths.destination = '.'
        for inc in self.opts.include:
            if not os.path.isdir(inc):
                logger.critical('Invalid path %r' % inc)
                return False
            config.paths.paths.append(inc)
        config.version = Version(1, 0)

        conf_xml = save_config(config)
        logger.debug('Equivalent configuration:')
        map(lambda line: logger.debug(line), conf_xml.split('\n'))
        if self.opts.config:
            conf_file = open(self.opts.config, 'w')
            conf_file.write(conf_xml)
            conf_file.close()

        Builder(FileResourceLocator('.')).build(config, target, force = True)
        return True
