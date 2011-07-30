import sys
import os
import os.path
import optparse

from codega.config import parse_config
from codega.error import ResourceError, ParseError
from codega.build import Builder
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
        # Load configuration file
        try:
            logger.info('Loading config file %r', self.opts.config)
            config = parse_config(filename = self.opts.config)

        except ParseError, parse_error:
            logger.error('Parse error (at line %s): %s' % (parse_error.lineno, parse_error.message))
            return False

        except ResourceError, rsc_error:
            logger.error('Config file not found: %r' % rsc_error.resource)
            return False

        if self.opts.target:
            build_list = [config.targets[t] for t in self.opts.target]

        else:
            build_list = config.targets.values()

        Builder().build_list(config, build_list, force = self.opts.target)
        return True
