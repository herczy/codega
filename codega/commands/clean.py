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
            optparse.make_option('-c', '--config', default = 'codega.xml',
                                 help = 'Specify config file (default: %default)'),
        ]

        super(CommandClean, self).__init__('clean', options, helpstring = 'Clean up codega targets and any additional files listed in the make file')

    def execute(self):
        return ConfigBuilder.run_make('cleanup', self.opts.config)
