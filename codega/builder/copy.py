'''
Build tasks handle the building of a target.
'''

import os.path
import stat

from codega.generator.base import GeneratorBase
from codega.context import Context
from codega.source import SourceBase
from codega.error import StateError

from base import TaskBase, phase
from time import get_mtime

class CopyTask(TaskBase):
    '''Build a configuration copy-target'''

    _config = None
    _locator = None
    _source = None
    _target = None

    def __init__(self, builder, config, locator, source, target):
        self._config = config
        self._locator = locator
        self._source = self._locator.find(source)
        self._target = os.path.join(self._locator.find(self._config.paths.destination), target)

        super(CopyTask, self).__init__(builder)

    @phase('build')
    def phase_build(self, phase_id, force):
        if not force and os.path.exists(self._target):
            if get_mtime(self._target) >= get_mtime(self._source):
                return

        # Write output
        destination = open(self._target, 'w')
        destination.write(open(self._source, 'r').read())
        destination.close()

    @phase('cleanup')
    def phase_cleanup(self, phase_id, force):
        if os.path.isfile(self._destination):
            os.remove(self._destination)
