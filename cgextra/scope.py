'''
:Date: 2011-09-06
:Version: 1
:Authors:
  - Viktor Hercinger <hercinger.viktor@gmail.com>

Implementation for keeping track of scopes. Scopes contain information about named objects
reachable from a point during generation.
'''

class Scope(object):
    '''
    Scope object to keep track of named objects.
    
    During generation some named objects should be reachable, like variable names, fields, etc.
    So when i.e. an expression references such an object through its name, this object will contain
    all information on it, be it a type, a field in a type, etc.
    
    The member `_parent` contains the parent scope and `_bindings` contains the scope elements. `_subscopes`
    contains the scopes depending on this one.  
    '''

    _parent = None
    _bindings = None
    _subscopes = None

    def __init__(self, parent = None):
        '''
        Initializes an empty scope.
        
        If `parent` is set, then everything that wasn't found here will be proxied to the
        `parent` object. This is accomplished through the `\\[\\]` operator.
        '''

        self._parent = parent
        self._bindings = {}
        self._subscopes = []

        if parent is not None:
            parent.add_subscope(self)

    def add_subscope(self, subscope):
        '''Add a sub-scope to this one. Do not call this directly'''

        self._subscopes.append(subscope)

    def is_subscope(self, subscope, recursive = True):
        '''Determine if a scope is a sub-scope of the current one'''

        if subscope in self._subscopes:
            return True

        if recursive and self._parent is not None and self._parent.is_subscope(subscope):
            return True

        return False

    def is_superscope(self, superscope, recursive = True):
        '''Determine if a scope is a super-scope of the current one'''

        if self._parent is None:
            return False

        if superscope is self._parent:
            return True

        if recursive and self._parent.is_superscope(superscope):
            return True

        return False

    @property
    def root(self):
        '''Get the root node.'''

        if self._parent is None:
            return self

        return self.parent.root

    @property
    def parent(self):
        '''Get the parent node.'''

        return self._parent

    @property
    def subscopes(self):
        '''Get the subscopes of the node.'''

        return self._subscopes

    def __getitem__(self, name):
        '''
        Get an entry from the scope. If `name` is not found in `_bindings`, try with the parent.
        If the parent scope doesn't have it either raise a `KeyError`.
        '''

        if self._bindings.has_key(name):
            return self._bindings[name]

        if self.parent is not None:
            return self.parent[name]

        raise KeyError("%s was not found in the current scope" % name)

    def __setitem__(self, name, value):
        '''Add `value` to the scope'''

        self._bindings[name] = value

    def __delitem__(self, name):
        '''Try to delete `name` in the current scope. If it could not be deleted, raise a `KeyError`'''

        if not self._bindings.has_key(name):
            raise KeyError("%s was not found in the current scope" % name)

        del self._bindings[name]

    def scope_of(self, name):
        '''Get the scope of the item `name`'''

        if self._bindings.has_key(name):
            return self

        if self._parent:
            return self._parent.scope_of(name)

        raise KeyError("%s was not found in the scopes" % name)

    def to_dict(self, recursive = True):
        '''Convert scope to dictionary (recursively if requested)'''

        res = dict(self._bindings)
        if recursive and self._parent:
            res.update(self._parent.to_dict(recursive = True))

        return res

class ScopeHandler(object):
    '''
    Handle multiple nested scopes.
    '''

    _scope_class = None
    _current_scope = None

    def __init__(self, scope_class = Scope):
        self._scope_class = scope_class
        self._current_scope = self._scope_class()

    def scope_of(self, key, try_only = False):
        '''Determine the scope of the key'''

        try:
            return self._current_scope.scope_of(key)

        except KeyError:
            if try_only:
                return None

            raise

    def push(self):
        '''Create a subscope of this scope.'''

        self._current_scope = self._scope_class(parent = self._current_scope)
        return self._current_scope

    def pop(self):
        '''Remove the current scope from the handler'''

        res = self._current_scope
        self._current_scope = res.parent

        return res

    def __enter__(self):
        '''Enter a new scope. Wrapper for `ScopeHandler.push()`.'''

        return self.push()

    def __exit__(self, *args):
        '''Exit the current scope. Wrapper for `ScopeHandler.pop()`'''

        self.pop()

    def __getitem__(self, name):
        '''Proxy to `Scope.__getitem__()`'''

        return self._current_scope[name]

    def __setitem__(self, name, value):
        '''Proxy to `Scope.__setitem__()`'''

        self._current_scope[name] = value

    def __delitem__(self, name):
        '''Proxy to `Scope.__delitem__()`'''

        del self._current_scope[name]

    def get(self, name, default = None):
        try:
            return self[name]

        except KeyError:
            return default

    def to_dict(self):
        '''Collapse scope and convert to dictionary'''

        return self._current_scope.to_dict()
