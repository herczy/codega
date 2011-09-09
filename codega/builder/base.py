'''
Base task
'''

from codega.decorators import collect_marked_bound, mark
from codega.error import StateError
from codega import logger

def job(job_id, depends = ()):
    '''Marks a function as a preparator for the given task'''

    return mark('task_job', (job_id, depends))

class TaskBase(object):
    '''Task base for building

    Members:
    _builder -- The parent of the task
    '''

    _builder = None

    def __init__(self, builder):
        self._builder = builder

    def list_supported_jobs(self):
        '''List the supported job ID's of the task'''

        res = set()
        for (job_id, depends), job in collect_marked_bound(self, 'task_job'):
            res.add(job_id)

        return tuple(res)

    def build(self, job_id, force = False, skip = None):
        '''Execute a job in the task'''

        # The skip list is a list of jobs that have been done in
        # this iteration so they don't need to be redone
        if skip is None:
            skip = []

        # Find the handler for the job
        handler = None
        dependencies = None
        for (_job_id, depends), job in collect_marked_bound(self, 'task_job'):
            if _job_id == job_id:
                if handler is not None:
                    raise StateError("More than one handlers for the job %s in %s" % (handler, self.__class__.__name__))

                handler = job
                dependencies = depends

        # No job by the given ID
        if handler is None:
            return

        # Watch out for circular references
        skip.append(job_id)

        # Build dependencies, watch for recursion
        for dep in dependencies:
            if dep in skip:
                logger.warning('Dependency %s already built' % dep)
                continue

            self.build(dep, force = force, skip = skip)

        handler(job_id, force)
