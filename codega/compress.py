'''Handle compressing the codega library and creating a script from it'''

import os
import sys
import os.path
import stat
import time

from hashlib import sha256
from tarfile import *
from base64 import b64encode

try:
    from cStringIO import StringIO

except ImportError:
    from StringIO import StringIO

def create_compressed_script(target):
    '''Create a script containing the compressed codega module and the main script

    Arguments:
    target -- Target file object
    '''

    def exclude_files(filename):
        print filename, (filename[-4:] == '.pyc' or os.path.basename(filename)[0] == '.')
        return (filename[-4:] == '.pyc' or os.path.basename(filename)[0] == '.')

    def compress(path):
        output = StringIO()
        tar = TarFile.open(fileobj = output, mode = 'w:bz2')
        tar.add(path, arcname = 'codega', exclude = exclude_files)
        tar.close()
        return output.getvalue()

    def checksum(data):
        return sha256(data).hexdigest()

    def split_data(data, line_width = 80):
        enc = b64encode(data)
        res = []
        while enc:
            line = '#>>' + enc[:line_width] + '<<'
            enc = enc[line_width:]
            res.append(line)

        return '\n'.join(res)

    data = compress(os.path.dirname(__file__))
    checksum = checksum(data)
    split = split_data(data)

    print >>target, '''#!/usr/bin/env python

import os
import os.path
import tarfile
import sys
import base64

outdir = '.codega-%(checksum)s'
outdir = os.path.join(os.path.dirname(__file__), outdir)

def check_decompress():
    global outdir

    try:
        from cStringIO import StringIO

    except ImportError:
        from StringIO import StringIO

    if os.path.isdir(outdir) and os.path.isdir(os.path.join(outdir, 'codega')):
        return

    if not os.path.isdir(outdir):
        if os.path.exists(outdir):
            raise Exception("%%s exists but is not a directory" %% outdir)

        data = ''.join(map(lambda l: l[3:-3], filter(lambda l: l[:3] == '#>>' and l[-3:] == '<<\\n', open(__file__))))
        data = base64.b64decode(data)

        os.mkdir(outdir)
        inobj = StringIO(data)
        tarfile.open(fileobj = inobj, mode = 'r:*').extractall(path = outdir)

sys.path.insert(0, outdir)
check_decompress()

from codega.build import Builder
Builder.main()

%(split)s
''' % locals()
