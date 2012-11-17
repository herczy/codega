import optparse

from codega.builder.config import run_make

from base import OptparsedCommand

class CommandClean(OptparsedCommand):
    _arg = None

    def __init__(self):
        options = [
            optparse.make_option('-c', '--config', default=None,
                                 help='Specify config file (default: codega or codega.xml)'),
        ]

        super(CommandClean, self).__init__('clean', options, helpstring='Clean up codega targets and any additional files listed in the make file')

    def execute(self):
        return run_make('cleanup', self.opts.config)
