import os.path
from codega.alp.script import parse_file

basedir = os.path.dirname(__file__)
langfile = os.path.join(basedir, 'alplang.alp')
module = parse_file(langfile)
