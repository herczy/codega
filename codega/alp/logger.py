from logging import getLogger
from codega.logger import ERROR, WARNING, TRACE


class IDMapper(object):
    '''Map object IDs to sequential, readable IDs. The first object registered will
    have an id of 0, the next 1, etc. This mapping is useful if classes need to be
    easily identifiable in logs, the output, etc. or just creating names automatically.'''

    def __init__(self):
        self._mapping = {}
        self._next_id = 0

    def map_object(self, object):
        '''Map an object. This creates the sequential ID for the supplied object.'''

        self._mapping[id(object)] = self._next_id
        self._next_id += 1

    def unmap_object(self, object):
        '''Unmap an object. The reference is removed from the current mapping. If the
        object is mapped again, the ID will be newly generated.'''

        objid = id(object)
        if objid in self._mapping:
            del self._mapping[objid]

    def get_id(self, object):
        '''Get the mapped ID of the object. If the object is not yet mapped, the function
        will map it.'''

        objid = id(object)
        if objid not in self._mapping:
            self.map_object(object)

        return self._mapping[objid]


# System mapping is the system namespace for maps
system_mapping = IDMapper()


def sysid(object):
    '''Get the mapped ID of an object.'''

    global system_mapping

    return system_mapping.get_id(object)


class Progress(object):
    '''Track the progress of an operation.'''

    def __init__(self, name, logfn, **info):
        self._name = name
        self._logfn = logfn
        self._info = dict(info)

        self._success = True

        self._info['Progress ID'] = sysid(self)

    def message(self, msg):
        '''Emit a message with the progress info.'''

        self._logfn('%s; %s' % (msg, ', '.join(map(lambda v: "%s='%s'" % v, self._info.items()))))

    def fail(self):
        '''Mark process as failed.'''

        self._success = False

    def __enter__(self):
        '''Start a progress.'''

        self.message('Starting: %s' % self._name)
        return self

    def __exit__(self, exc_type, exc_value, trace):
        '''Exit a progress.'''

        if exc_type:
            self.message("Exception caught during process '%s'" % self._name)

        elif not self._success:
            self.message("Process '%s' ended with error" % self._name)

        else:
            self.message("Process '%s' succeeded" % self._name)


def make_proxy_caller(level):
    '''Make a proxy caller for the ply logger.'''

    def __wrapper(self, *args, **kwargs):
        self.log(level, *args, **kwargs)

    return __wrapper


class PlyLoggerWrapping(object):
    '''Wrap ply/lex logging.'''

    def __init__(self, log):
        self._log = log

    def log(self, level, msg, *args, **kwargs):
        self._log.log(level, msg % args)

    error = make_proxy_caller(ERROR)
    critical = error
    warning = make_proxy_caller(WARNING)
    info = make_proxy_caller(TRACE)
    debug = make_proxy_caller(TRACE)
