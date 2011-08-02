import os
import os.path

from hashlib import sha256
from tarfile import TarFile
from base64 import b64encode

try:
    from cStringIO import StringIO

except ImportError:
    from StringIO import StringIO

import codega
from codega import logger

from base import CommandBase

class CommandPack(CommandBase):
    _arg = None

    def __init__(self):
        super(CommandPack, self).__init__('pack', helpstring = 'Create a script containing the compressed codega module and the main script')

    def create_compressed_script(self, target):
        '''Create a script containing the compressed codega module and the main script

        Arguments:
        target -- Target file object
        '''

        def exclude_files(filename):
            exclude = (filename[-4:] == '.pyc' or os.path.basename(filename)[0] == '.')
            if exclude:
                logger.debug('File %r not included', filename)

            else:
                logger.info('Adding file %r', filename)

            return exclude

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

        def load_main_code():
            '''Load cgmake code'''

            cgmake = []
            start = False

            for i in open(__file__):
                i = i.rstrip()

                if i[:6] == '# MARK':
                    start = True
                    continue

                if not start:
                    continue

                cgmake.append(i)

            return '\n'.join(cgmake)

        logger.info('Creating self-contained script')
        logger.info('Compressing codega path %r', os.path.dirname(codega.__file__))
        data = compress(os.path.dirname(codega.__file__))
        checksum = checksum(data)
        logger.info('Data compressed, checksum is %s' % checksum)
        split = split_data(data)
        main_code = load_main_code()

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

%(main_code)s

%(split)s
''' % locals()
        logger.info('Self-contained script created')

    def prepare(self, argv):
        if len(argv) != 1:
            critical("Wrong number of arguments (usage: pack <output>)")
            return False

        self._arg = argv[0]

    def execute(self):
        out = open(self._arg, 'w')
        self.create_compressed_script(out)
        out.close()

        os.chmod(self._arg, 0755)

        logger.info('Output %r created', self._arg)
        return True
