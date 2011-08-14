'''Generate a Python script for dumping the data'''

from codega.generator import ObjectGenerator, FunctionGenerator, FilterGenerator

from cgextra.makowrapper import inline
from cgextra.indent import indent
from cgextra import matcher

class PyGen(ObjectGenerator):
    @inline(matcher = matcher.root)
    def generate_root(self, source, context):
        '''
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
                    
                return '\\n'.join(res)

        print Data(
        % for row in rows:
          ${row},
        % endfor
        ).dump()
        '''

        return dict(rows = context.map(self, source))

    @FilterGenerator.decorate(lambda generator, text: indent(text, indent_string = '    '))
    @inline(matcher.tag('row'))
    def generate_row(self, source, context):
        '''
        DataRow(
        % for entry in entries:
          ${entry},
        % endfor
        )'''

        return dict(entries = context.map(self, source))

    @FilterGenerator.decorate(lambda generator, text: indent(text, indent_string = '    '))
    @FunctionGenerator.decorate(matcher.tag('entry'))
    def generate_entry(self, source, context):
        return 'DataEntry("""%s""")' % source.text
