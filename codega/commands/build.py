import optparse

from codega.builder.config import ConfigBuilder

from base import OptparsedCommand

class CommandBuild(OptparsedCommand):
    def __init__(self):
        options = [
            optparse.make_option('-s', '--source', default = None,
                                 help = 'Specify the source (file, directory, etc., depending on the parser)'),
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

            optparse.make_option('-S', '--set', default = [], action = 'append',
                                 help = 'Append custom settings in the form of key=value')
        ]

        super(CommandBuild, self).__init__('build', options, helpstring = 'Build the source with specified generator')

    def execute(self):
        return ConfigBuilder.run_build('build', self.opts.source, self.opts.parser, self.opts.target, self.opts.generator, includes = self.opts.include, config_dest = self.opts.config, settings = self.opts.set)
