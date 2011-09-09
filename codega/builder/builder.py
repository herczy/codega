'''
Builders are classes controlling the build process
'''

from codega.error import BuildError
from codega import logger

class Builder(object):
    '''Base object for builders

    Members:
    _cache -- Source cache for parse results
    _tasks -- Task backlog
    '''

    _cache = None
    _tasks = None

    def __init__(self):
        self._cache = {}
        self._tasks = []

    def push_task(self, task):
        '''Add a task to the task list'''

        self._tasks.append(task)

    def build(self, job_id, force = False):
        '''Build tasks.

        Note that the tasks will be removed!
        '''

        try:
            for task in self._tasks:
                logger.debug('Running job %s on task %s' % (job_id, task))
                task.build(job_id, force = force)

        except Exception, e:
            logger.exception(preface = 'Build error', line_prefix = '** ')
            raise BuildError('Error detected during build: %s' % e)
