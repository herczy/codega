'''Matchers are objects that return true if the source meets some conditions'''

import operator

class MatcherBase(object):
    '''Matcher base class'''

    def __call__(self, source):
        '''Match check call'''

        raise NotImplementedError('MatcherBase.__call__ is abstract')

    def __not__(self):
        return CombinedMatcher(operator.__not__, self)

    def __and__(self, other):
        return CombinedMatcher(operator.__and__, self, other)

    def __or__(self, other):
        return CombinedMatcher(operator.__or__, self, other)

    def __xor__(self, other):
        return CombinedMatcher(operator.__xor__, self, other)

class FunctionMatcher(MatcherBase):
    '''MatcherBase wrapper for functions

    Members:
    _function -- Match function
    '''

    _function = None

    def __init__(self, func):
        super(FunctionMatcher, self).__init__()

        self._function = func

    def __call__(self, source):
        return self._function(source)

class CombinedMatcher(MatcherBase):
    '''Emulates a result

    Members:
    _operand -- Result combining function
    _arguments -- Other matchers whose results get combined
    '''

    _operand = None
    _arguments = None

    def __init__(self, operand, *arguments):
        self._operand = operand
        self._arguments = arguments

    def __call__(self, source):
        return self._operand(*map(lambda matcher: matcher(source), self._arguments))

matcher = FunctionMatcher

@matcher
def all(source):
    return True

@matcher
def none(source):
    return False

@matcher
def comment(source):
    return isinstance(source, etree._Comment)

def tag(tag):
    @matcher
    def __matcher(source):
        return source.tag == tag

    return __matcher

def xpath(xpath):
    xpath = etree.XPath(xpath)

    @matcher
    def __matcher(source):
        return source in xpath(source)

    return __matcher

def cls(cls):
    @matcher
    def __matcher(source):
        return isinstance(source, cls)

    return __matcher
