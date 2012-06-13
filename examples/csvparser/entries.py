class DataEntry(object):
    def __init__(self, value):
        self._value = value

    def dump(self, padding = 0):
        return '%s%s' % (self._value, ' ' * (padding - len(self._value)))

    def __len__(self):
        return len(self._value)

class DataRow(object):
    def __init__(self, *entries):
        self._entries = entries

    def dump(self, separator, *paddings):
        return separator.join(map(lambda (s, p): s.dump(padding = p), zip(self._entries, paddings)))

    def __len__(self):
        return len(self._entries)

    entries = property(lambda self: self._entries)

class Data(object):
    def __init__(self, *rows):
        self._rows = rows

    def dump(self):
        maxes = []

        for row in self._rows:
            if len(row) > len(maxes):
                for i in xrange(len(row) - len(maxes)):
                    maxes.append(0)

            for ndx, entry in enumerate(row.entries):
                maxes[ndx] = max(maxes[ndx], len(entry))

        res = []
        for row in self._rows:
            res.append(row.dump(' | ', *maxes))

        return '\n'.join(res)

print Data(
      DataRow(
          DataEntry("""Product code"""),
          DataEntry("""Price ($)"""),
          DataEntry("""Pieces (pcs)"""),
          DataEntry("""Total ($)"""),
    ),
      DataRow(
          DataEntry("""#12124"""),
          DataEntry("""10"""),
          DataEntry("""100"""),
          DataEntry("""1000"""),
    ),
      DataRow(
          DataEntry("""#56634"""),
          DataEntry("""42"""),
          DataEntry("""100"""),
          DataEntry("""4200"""),
    ),
).dump()
