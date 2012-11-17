import optparse

from codega.builder.config import run_make

from base import OptparsedCommand

class CommandMake(OptparsedCommand):
    _arg = None

    def __init__(self):
        options = [
            optparse.make_option('-c', '--config', default=None,
                                 help='Specify config file (default: codega or codega.xml)'),
            optparse.make_option('-t', '--target', default=[], action='append',
                                 help='Specify targets (default: all)'),
            optparse.make_option('-f', '--force', default=False, action='store_true',
                                 help='Force rebuild'),
        ]

        super(CommandMake, self).__init__('make', options, helpstring='Build codega targets listed in the make file')

    def execute(self):
        return run_make('build', self.opts.config, targets=tuple(self.opts.target), force=self.opts.force)
