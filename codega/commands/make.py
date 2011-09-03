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
            optparse.make_option('-c', '--config', default = 'codega.xml',
                                 help = 'Specify config file (default: %default)'),
            optparse.make_option('-t', '--target', default = [], action = 'append',
                                 help = 'Specify targets (default: all)'),
            optparse.make_option('-f', '--force', default = False, action = 'store_true',
                                 help = 'Force rebuild'),
        ]

        super(CommandMake, self).__init__('make', options, helpstring = 'Build codega targets listed in the make file')

    def execute(self):
        return ConfigBuilder.run_make('build', self.opts.config, targets = tuple(self.opts.target), force = self.opts.force)
