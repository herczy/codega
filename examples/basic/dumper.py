from codega.generator.base import GeneratorBase
from codega.version import Version

from cStringIO import StringIO

def indent(txt):
    res = []
    for line in txt.split('\n'):
        if line:
            res.append('  %s' % line)

        else:
            res.append('')

    return '\n'.join(res)

class DumpGenerator(GeneratorBase):
    def generate(self, source, context):
        def _(d, x):
            print >>d, '%s: %s' % (x.tag, ', '.join(map(lambda a: '%s = %r' % a, x.attrib.iteritems())))
            if x.text:
                print >>d, indent('text = \'\'\'%s\'\'\'' % x.text)

            print >>d, '{'
            for c in x:
                r = StringIO()
                _(r, c)
                d.write(indent(r.getvalue()))

            print >>d, '}'

        io = StringIO()
        _(io, source)
        return io.getvalue()
