'''
Proxy tasks call other objects

'''

from base import TaskBase

class ProxyTask(TaskBase):
    '''Wrap function as a task'''

    def __init__(self, builder, build_function):
        self._build_function = build_function

        super(ProxyTask, self).__init__(builder)

    def build(self, job_id, force = False, skip = None):
        self._build_function(job_id = job_id, force = force)
