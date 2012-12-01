import optparse

from codega.config.structures import StructureBuilder
from codega.config.saver import save_config
from codega.builder import BuildRunner
from codega import logger

from base import OptparsedCommand


class CommandBuild(OptparsedCommand):
    def __init__(self):
        options = [
            optparse.make_option('-s', '--source', default=None,
                                 help='Specify the source (file, directory, etc., depending on the parser)'),
            optparse.make_option('-p', '--parser', default='codega.source:XmlSource',
                                 help='Specify the parser in <module>:<source class> format (default: %default)'),
            optparse.make_option('-t', '--target', default='codega.out',
                                 help='Specify the target file (default: %default)'),
            optparse.make_option('-g', '--generator', default=None,
                                 help='Specify the generator in <module>:<source class> format'),

            optparse.make_option('-I', '--include', default=['.'], action='append',
                                 help='Add a new search path (for modules, sources, etc.)'),

            optparse.make_option('-c', '--config', default=None,
                                 help='Write the equivalent config to the given file'),

            optparse.make_option('-S', '--set', default=[], action='append',
                                 help='Append custom settings in the form of key=value')
        ]

        super(CommandBuild, self).__init__('build', options, helpstring='Build the source with specified generator')

    def execute(self):
        config_builder = StructureBuilder()
        config_builder.add_source('source', self.opts.source, parser=self.opts.parser)
        config_builder.add_target('source', self.opts.target, self.opts.generator)
        config_builder.set_destination('.')

        for inc in self.opts.include:
            config_builder.add_include(inc)

        for setting in self.opts.set:
            if '=' not in setting:
                logger.critical('Invalid setting %r' % setting)
                return False

            key, value = setting.split('=', 1)
            config_builder.add_setting(self.opts.target, key, value)

        config = config_builder.config

        # Save config if requested
        if self.opts.config is not None:
            conf_xml = save_config(config)
            with open(self.opts.config, 'w') as out:
                out.write(conf_xml)

        return BuildRunner(config).run_task('build', force=True)
