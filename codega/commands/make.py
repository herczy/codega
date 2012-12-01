import optparse

from codega.builder import BuildRunner

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

    def filter(self, name):
        if self.opts.target:
            return name in self.opts.target

        return True

    def execute(self):
        return BuildRunner.run_task_file(self.opts.config, 'build', filter=self.filter, force=self.opts.force)
