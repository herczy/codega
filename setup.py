#!/usr/bin/env python

import os
try:
    from setuptools import setup

except ImportError:
    from distutils.core import setup

if os.system('./cgx make -c codega/alp/codega.xml'):
    exit(1)

setup(name = "codega",
        description = "Codega code generator framework",
        long_description = """File generator toolkit written in Python

Codeca can be used to generate files from XML inputs using rules
described in Python. The Python handler classes handle each XML node
and generate the corresponding file segment. These segments are then
combined to form the output.

Mainly intended to parse XML files describing data structures and
then generating the serialize/deserialize code in various languages,
but mostly C/C++. However it can be easily used for other purposes
""",
        license = "BSD",
        version = open("VERSION").read().strip(),
        author = "Viktor Hercinger",
        author_email = "hercinger.viktor@gmail.com",
        maintainer = "Viktor Hercinger",
        maintainer_email = "hercinger.viktor@gmail.com",
        packages = [ 'codega',
                     'codega.config',
                     'codega.commands',
                     'codega.generator',
                     'codega.alp',
                     'codega.alp.generator' ],
        package_data = { 'codega' : [ 'config.xsd' ],
                         'codega.alp' : [ 'alplang.alp' ],
                         'codega.alp.generator' : [ 'scriptgen.mako' ] },
        scripts = [ 'cgx' ],
        requires = [ 'lxml' ])
