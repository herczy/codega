'''Create a new AST module run-time'''

import types

from codega.decorators import collect_marked_bound

from base import AstType, AstBase

class ModuleCreator(object):
    '''A creator for AST modules'''

    def __init__(self, name):
        self._module = types.ModuleType(name)
        self._module.validators = {}
        self._module.types = {}

    def load_validator(self, name, validators):
        '''Make a validator'''

        self._module.validators[name] = validators

    def load_validator_dict(self, validator):
        '''Load validators from the given dictionary'''

        self._module.validators.update(validator)

    def load_validator_module(self, validator_module):
        '''Load validators from a Python module'''

        for name, validator in collect_marked_bound(validator_module, 'validator'):
            self.load_validator(name, validator)

    def make_type(self, name, required = (), optional = (), validate = {}, base = None):
        '''Add an AST type to the module'''

        if base is None:
            base = AstBase

        if isinstance(base, basestring):
            base = getattr(self._module, base)

        self._module.types[name] = AstType(name, (base,), dict(_required = required, _optional = optional, _validate = validate))
        setattr(self._module, name, self._module.types[name])

    @property
    def validators(self):
        '''Get the validator dictionary'''

        return self._module.validators

    @property
    def types(self):
        '''Get the type dict'''

        return self._module.types

    @property
    def module(self):
        '''Get the module'''

        return self._module
