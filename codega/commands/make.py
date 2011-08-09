import sys
import os
import os.path
import optparse

from codega.config import parse_config_file
from codega.error import ResourceError, ParseError
from codega.build import Builder, ConfigBuilder
from codega.rsclocator import FileResourceLocator
from codega import logger

from base import OptparsedCommand

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
        # Check if file exists
        if not os.path.isfile(self.opts.config):
            logger.critical("File %r not found", self.opts.config)
            return False

        # Locator from the config file
        locator = FileResourceLocator(os.path.dirname(self.opts.config))

        # Load configuration file
        try:
            logger.info('Loading config file %r', self.opts.config)
            config = parse_config_file(self.opts.config)

        except ParseError, parse_error:
            logger.error('Parse error (at line %s): %s' % (parse_error.lineno, parse_error.message))
            return False

        if self.opts.target:
            build_list = [config.targets[t] for t in self.opts.target]

        else:
            build_list = config.targets.values()

        config_builder = ConfigBuilder(config, locator)
        for target in build_list:
            config_builder.add_target(target)
        config_builder.build(force = self.opts.force)
        return True
