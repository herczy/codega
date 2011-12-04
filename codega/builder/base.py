'''
Base task
'''

from codega.decorators import collect_marked_bound, mark
from codega.error import StateError
from codega import logger

def phase(phase_id, depends = ()):
    '''Marks a function as a preparator for the given task'''

    return mark('task_phase', (phase_id, depends))

class TaskBase(object):
    '''Task base for building

    Members:
    _builder -- The parent of the task
    '''

    _builder = None

    def __init__(self, builder):
        self._builder = builder

    def list_supported_phases(self):
        '''List the supported phase ID's of the task'''

        res = set()
        for (phase_id, depends), phase in collect_marked_bound(self, 'task_phase'):
            res.add(phase_id)

        return tuple(res)

    def build(self, phase_id, force = False, skip = None):
        '''Execute a phase in the task'''

        # The skip list is a list of phases that have been done in
        # this iteration so they don't need to be redone
        if skip is None:
            skip = []

        # Find the handler for the phase
        handler = None
        dependencies = None
        for (_phase_id, depends), phase in collect_marked_bound(self, 'task_phase'):
            if _phase_id == phase_id:
                if handler is not None:
                    raise StateError("More than one handlers for the phase %s in %s" % (handler, self.__class__.__name__))

                handler = phase
                dependencies = depends

        # No phase by the given ID
        if handler is None:
            return

        # Watch out for circular references
        skip.append(phase_id)

        # Build dependencies, watch for recursion
        for dep in dependencies:
            if dep in skip:
                logger.warning('Dependency %s already built' % dep)
                continue

            self.build(dep, force = force, skip = skip)

        handler(phase_id, force)
