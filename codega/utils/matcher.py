'''Matchers are objects that return true if the source meets some conditions'''

import operator

from lxml import etree

from decorators import abstract

class MatcherBase(object):
    '''Matcher base class'''

    @abstract
    def __call__(self, source, context):
        '''Match check call'''

    @property
    def neg(self):
        return CombinedMatcher(operator.__not__, self)

class FunctionMatcher(MatcherBase):
    '''MatcherBase wrapper for functions

    Members:
    _function -- Match function
    '''

    _function = None

    def __init__(self, func):
        super(FunctionMatcher, self).__init__()

        self._function = func

    def __call__(self, source, context):
        return self._function(source, context)

class CombinedMatcher(MatcherBase):
    '''Emulates a result

    Members:
    _operator -- Result combining function
    _arguments -- Other matchers whose results get combined
    '''

    _operator = None
    _arguments = None

    def __init__(self, operantor, *arguments):
        self._operator = operantor
        self._arguments = arguments

    def __call__(self, source, context):
        return self._operator(*map(lambda matcher: matcher(source, context), self._arguments))

matcher = FunctionMatcher

@matcher
def true(source, context):
    return True

@matcher
def false(source, context):
    return False

@matcher
def comment(source, context):
    return isinstance(source, etree._Comment)

def tag(tag):
    @matcher
    def __matcher(source, context):
        return source.tag == tag

    return __matcher

def parent(tag):
    @matcher
    def __matcher(source, context):
        parent = source.getparent()
        if parent is None:
            return tag is None

        return parent.tag == tag

    return __matcher
root = parent(None)

def xpath(xpath):
    xpath = etree.XPath(xpath)

    @matcher
    def __matcher(source, context):
        return source in xpath(source)

    return __matcher

def cls(cls):
    @matcher
    def __matcher(source, context):
        return isinstance(source, cls)

    return __matcher

def any(*matchers):
    @matcher
    def __matcher(source, context):
        for matcher in matchers:
            if matcher(source, context):
                return True

        return False

    return __matcher

def all(*matchers):
    @matcher
    def __matcher(source, context):
        for matcher in matchers:
            if not matcher(source, context):
                return False

        return True

    return __matcher
