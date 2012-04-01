import os.path

if 0:
    from codega.alp.script import parse_file
    basedir = os.path.dirname(__file__)
    langfile = os.path.join(basedir, 'alplang.alp')
    module = parse_file(langfile)

else:
    from codega.alp import script
    module = script
    module.baseclass = script.AstBaseClass
