'''
Configuration builder, is a facade to the build sub-system
'''

import os.path

from codega import logger
from codega.config.structures import StructureBuilder
from codega.config.saver import save_config
from codega.config.loader import ConfigLoader

from codega.rsclocator import FallbackLocator, FileResourceLocator
from codega.error import ParseError
from codega.builder.copy import CopyTask

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

    def add_external(self, external, targets=(), force=False):
        task = ProxyTask(self, lambda phase_id, force: run_make(phase_id, external, targets=targets, force=force))
        self.push_task(task)

    def add_copy(self, copy):
        task = CopyTask(self, copy.parent, self._locator, copy.source, copy.target)
        self.push_task(task)


def get_config(config_file):
    if config_file is None:
        if os.path.isfile('codega'):
            return 'codega'

        elif os.path.isfile('codega.xml'):
            return 'codega.xml'

    else:
        if os.path.isfile(config_file):
            return config_file


def run_make(phase_id, opt_config_file=None, targets=(), force=False):
    config_file = get_config(opt_config_file)

    # Check if file exists
    if config_file is None:
        if opt_config_file:
            logger.critical("File %r not found", opt_config_file)

        else:
            logger.critical("No suitable config file could be found")

        return False

    # Locator from the config file
    base_locator = FileResourceLocator(os.path.dirname(config_file))

    # Load configuration file
    try:
        logger.info('Loading config file %r', config_file)
        config = ConfigLoader().load(config_file)

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
        logger.debug('Adding external %s' % external)
        config_builder.add_external(external, targets=targets, force=force)

    # ... and with targets
    for target in build_list:
        logger.debug('Adding target %s' % target.filename)
        config_builder.add_target(target)

    # ... and with copy list
    for copy in config.copy.values():
        logger.debug('Adding copy task %s' % copy.target)
        config_builder.add_copy(copy)

    # Run build for targets
    config_builder.build(phase_id, force=force)
    return True


def run_build(phase_id, source, parser, target, generator, includes=(), config_dest=None, settings=None):
    if not source:
        logger.critical('Missing source')
        return False

    if not generator:
        logger.critical('Missing generator')
        return False

    config_builder = StructureBuilder()

    config_builder.add_source('source', source, parser=parser)
    build_target = config_builder.add_target('source', target, generator)
    for inc in includes:
        if not os.path.isdir(inc):
            logger.critical('Invalid path %r' % inc)
            return False

        config_builder.add_include(inc)

    if settings != None:
        for setting in settings:
            key, value = setting.split('=', 1)
            config_builder.add_setting(build_target, key, value)

    config = config_builder.config

    # Save config if requested
    if config_dest is not None:
        conf_xml = save_config(config)

        if config_dest:
            conf_file = open(config_dest, 'w')
            conf_file.write(conf_xml)
            conf_file.close()

    config_builder = ConfigBuilder(config, FileResourceLocator('.'))
    config_builder.add_target(build_target)
    config_builder.build(phase_id, force=True)
    return True
