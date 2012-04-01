import sys
sys.path.insert(0, '..')

from alpgenerator import alplang, validator, flatten

ast = alplang.module.parse_file('./alplang.alp')
ast = flatten(ast)
try:
    validator.Validator.run(ast)

except:
    raise

else:
    print 'Validation ok'
