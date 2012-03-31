LEFT = 0
RIGHT = 1

class RuleEntry(object):
    def __init__(self, name, ignore=None, key=None):
        self.name = name
        self.ignore = ignore
        self.key = key

    def __str__(self):
        entstr = self.name
        if self.ignore:
            entstr = '-' + entstr

        elif self.key:
            entstr = '%s=%s' % (self.key, entstr)

        return entstr

    def __repr__(self):
        return 'RuleEntry(%s)' % self

class Rule(object):
    def __init__(self, name, *entries):
        if not isinstance(name, basestring):
            raise ValueError("Name must be a string")

        self.name = name
        self.entries = entries
        self.precedence = None

    def to_yacc_rule(self):
        res = '%s : %s' % (self.name, ' '.join(e.name for e in self.entries))

        if self.precedence is not None:
            res += ' %%prec %s' % self.precedence

        return res

    def create_argument_list(self, values):
        args = []
        kwargs = {}

        values = list(values)

        for entry in self.entries:
            val = values[0]
            del values[0]

            if entry.ignore:
                continue

            if entry.key:
                kwargs[entry.key] = val

            else:
                args.append(val)

        if len(values):
            raise ValueError("Not all arguments have been parsed")

        return tuple(args), kwargs

    def __call__(self, func, values):
        args, kwargs = self.create_argument_list(values)
        return func(*args, **kwargs)

    def __str__(self):
        entries = (str(e) for e in self.entries)

        return '%s -> %s' % (self.name, ' '.join(entries))

    def __repr__(self):
        return 'Rule(%s)' % self
