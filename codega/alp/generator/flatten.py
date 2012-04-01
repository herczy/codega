from codega.alp import script

## THIS IS ONLY TEMPORARILY HERE UNTIL THE LIST FEATURE IS ADDED
def flatten(ast):
    if not isinstance(ast, script.AstBaseClass):
        return ast

    if set(ast.properties.keys()) == set(('entry', 'next')):
        tail = ()
        if ast.properties.next:
            tail = flatten(ast.properties.next)

        if ast.properties.entry:
            res = (flatten(ast.properties.entry),) + tail

        else:
            res = tail

        return res

    new_properties = dict(ast.map(lambda k, v: flatten(v)))
    return ast.__class__(**new_properties)
