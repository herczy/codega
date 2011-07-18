'''codega specific exceptions'''

class ParameteredError(Exception):
    '''Error with one or more parameters

    Arguments:
    _parameters -- Dictionary of additional parameters
    '''

    _parameters = None

    def __init__(self, msg, **params):
        super(ParameteredError, self).__init__(msg)

        self._parameters = dict(params)

    def __str__(self):
        parms = map(lambda (k, v): '%s = %r' % (k, v), filter(lambda (k, v): v is not None, self._parameters.iteritems()))
        prefix = super(ParameteredError, self).__str__()
        if not parms:
            return prefix

        return '%s (%s)' % (prefix, ', '.join(parms))

    def __repr__(self):
        parms = map(lambda (k, v): '%s = %r' % (k, v), filter(lambda (k, v): v is not None, self._parameters.iteritems()))
        parms.insert(0, 'message = %r' % self.message)
        return '%s(%s)' % (self.__class__.__name__, ', '.join(parms))

class ResourceError(ParameteredError):
    '''Resource error, thrown when a resource is not found'''

    def __init__(self, msg, resource = None):
        super(ResourceError, self).__init__(msg, resource = resource)

class TemplateNotFoundError(ParameteredError):
    '''Thrown when a template is not found in the collection'''

    def __init__(self, msg, tplset = None):
        super(TemplateNotFoundError, self).__init__(msg, tplset = tplset)

class VersionMismatchError(Exception):
    '''The version isn't what it supposed to be'''

class StateError(Exception):
    '''The state of the object is not what it's supposed to be'''
