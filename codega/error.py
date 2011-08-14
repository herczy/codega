'''codega specific exceptions'''

class ResourceError(Exception):
    '''Resource error, thrown when a resource is not found'''

    def __init__(self, msg, resource):
        super(ResourceError, self).__init__("%s (resource = %r)" % (msg, resource))

class TemplateNotFoundError(Exception):
    '''Thrown when a template is not found in the collection'''

    def __init__(self, msg, tplset):
        super(TemplateNotFoundError, self).__init__("%s (template set = %r)" % (msg, tplset))

class ConfigError(Exception):
    ''''The configuration is invalid'''

class ParseError(ConfigError):
    '''The given source could not be parsed'''

    def __init__(self, msg, lineno):
        super(ParseError, self).__init__("%s (at line %d)" % (msg, lineno))

class VersionMismatchError(Exception):
    '''The version isn't what it supposed to be'''

class StateError(Exception):
    '''The state of the object is not what it's supposed to be'''
