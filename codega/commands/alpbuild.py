import optparse

from base import OptparsedCommand
from codega.config.structures import * #@UnusedWildImports
from codega.builder.config import ConfigBuilder

class CommandAlpBuild(OptparsedCommand):
    def __init__(self):
        options = [
            optparse.make_option('-s', '--source', default='/dev/stdin',
                                 help='Specify the source (default: stdin)'),
            optparse.make_option('-t', '--target', default='/dev/stdout',
                                 help='Specify the target file (default: stdout)'),
            optparse.make_option('-I', '--include', default=['.'], action='append',
                                 help='Add a new search path (for modules, sources, etc.)'),
        ]

        super(CommandAlpBuild, self).__init__('alp-build', options, helpstring='Build ALP sources')

    def execute(self):
        return ConfigBuilder.run_build('build', self.opts.source, 'codega.alp.generator:ScriptParser', self.opts.target, 'codega.alp.generator:main_generator', self.opts.include)
