'''
Configuration builder, is a facade to the build sub-system
'''

import os.path

from codega import logger
from codega.config import Config, Source, Target, parse_config_file, save_config
from codega.rsclocator import FallbackLocator, FileResourceLocator
from codega.error import ParseError
from codega.version import Version

from builder import Builder
from target import TargetTask
from proxy import ProxyTask

class ConfigBuilder(Builder):
    '''Build targets from a config
    
    Members:
    _config -- Configuration for builder
    _locator -- Base locator for builder
    '''

    _config = None
    _locator = None

    def __init__(self, config, base_locator):
        self._config = config

        # Make locator
        self._locator = FallbackLocator()
        for path in config.paths.paths:
            self._locator.add_locator(FileResourceLocator(base_locator.find(path)))

        super(ConfigBuilder, self).__init__()

    def add_target(self, target):
        '''Add a configuration target'''

        config = target.parent
        source = config.sources[target.source]
        task = TargetTask(self, config, self._locator, source, target, self._cache)

        self.push_task(task)

    def add_external(self, external, targets = (), force = False):
        task = ProxyTask(self, lambda job_id, force: ConfigBuilder.run_make(job_id, external, targets = targets, force = force))
        self.push_task(task)

    @staticmethod
    def run_make(job_id, config_file, targets = (), force = False):
        #import pdb; pdb.set_trace()
        # Check if file exists
        if not os.path.isfile(config_file):
            logger.critical("File %r not found", config_file)
            return False

        # Locator from the config file
        base_locator = FileResourceLocator(os.path.dirname(config_file))

        # Load configuration file
        try:
            logger.info('Loading config file %r', config_file)
            config = parse_config_file(config_file)

        except ParseError, parse_error:
            logger.error('Parse error: %s', parse_error)
            return False

        # Populate list of build targets
        if targets:
            build_list = [config.targets[t] for t in targets]

        else:
            build_list = config.targets.values()

        # Populate external dependency list
        externals = list(config.external)

        # Populate config builder
        config_builder = ConfigBuilder(config, base_locator)

        # ... with externals
        for external in externals:
            config_builder.add_external(external, targets = targets, force = force)

        # ... and with targets
        for target in build_list:
            logger.debug('Adding target %s' % target.filename)
            config_builder.add_target(target)

        # Run build for targets
        config_builder.build(job_id, force = force)
        return True

    @staticmethod
    def run_build(job_id, source, parser, target, generator, includes = (), config_dest = None):
        if not source:
            logger.critical('Missing source')
            return False

        if not generator:
            logger.critical('Missing generator')
            return False

        config = Config()

        # Create source object
        source_obj = Source(config)
        source_obj.name = 'source'
        source_obj.resource = source
        if parser:
            source_obj.parser.load_from_string(parser)
        config.sources[source_obj.name] = source_obj

        # Create target object
        target_obj = Target(config)
        target_obj.source = 'source'
        target_obj.filename = target
        target_obj.generator.load_from_string(generator)
        config.targets[target_obj.filename] = target_obj

        # Create include list
        config.paths.destination = '.'
        for inc in includes:
            if not os.path.isdir(inc):
                logger.critical('Invalid path %r' % inc)
                return False
            config.paths.paths.append(inc)
        config.version = Version(1, 0)

        # Save config if requested
        if config_dest is not None:
            conf_xml = save_config(config)

            if config_dest:
                conf_file = open(config_dest, 'w')
                conf_file.write(conf_xml)
                conf_file.close()

        config_builder = ConfigBuilder(config, FileResourceLocator('.'))
        config_builder.add_target(target_obj)
        config_builder.build(job_id, force = True)
        return True

