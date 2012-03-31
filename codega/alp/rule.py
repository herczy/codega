class RuleEntry(object):
    def __init__(self, name, ignore=None, key=None):
        self.name = name
        self.ignore = ignore
        self.key = key

class Rule(object):
    def __init__(self, name, *entries):
        if not isinstance(name, basestring):
            raise ValueError("Name must be a string")

        self.name = name
        self.entries = entries

    def to_yacc_rule(self):
        return '%s : %s' % (self.name, ' '.join(e.name for e in self.entries))

    def create_argument_list(self, values):
        args = []
        kwargs = {}

        values = list(values)

        for entry in self.entries:
            if entry.key:
                kwargs[entry.key] = values[0]

            else:
                args.append(values[0])

            del values[0]

        if len(values):
            raise ValueError("Not all arguments have been parsed")

        return tuple(args), kwargs

    def __call__(self, func, values):
        args, kwargs = self.create_argument_list(values)
        return func(*args, **kwargs)

    def __str__(self):
        entries = []
        for entry in self.entries:
            entstr = entry.name
            if entry.ignore:
                entstr = '-' + entstr

            elif entry.key:
                entstr = '%s=%s' % (entry.key, entstr)

        return '%s -> %s' % (self.name, ' '.join(entries))
