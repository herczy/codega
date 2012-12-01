'''Parser generator for ALP descriptor files.\

This parser generator relies heavily on ply.lex and
ply.yacc. The supplied generator generates the lex and
yacc classes needed to parse the input and the resulting
AST classes.
'''

from scriptgen import main_generator
from scriptsource import ScriptParser
