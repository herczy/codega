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

class CommandClean(OptparsedCommand):
    _arg = None

    def __init__(self):
        options = [
            optparse.make_option('-c', '--config',  default = 'codega.xml',
                                 help = 'Specify config file (default: %default)'),
        ]

        super(CommandClean, self).__init__('clean', options, helpstring = 'Clean up codega targets and any additional files listed in the make file')

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

        config_builder = ConfigBuilder(config, locator)
        for target in config.targets.values():
            config_builder.add_target(target)
        config_builder.cleanup()
        return True
