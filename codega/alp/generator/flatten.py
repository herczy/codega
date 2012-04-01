from codega.alp import script

## THIS IS ONLY TEMPORARILY HERE UNTIL THE LIST FEATURE IS ADDED
def flatten(ast, base):
    if not isinstance(ast, base):
        return ast

    if set(ast.properties.keys()) == set(('entry', 'next')):
        tail = ()
        if ast.properties.next:
            tail = flatten(ast.properties.next, base)

        if ast.properties.entry:
            res = (flatten(ast.properties.entry, base),) + tail

        else:
            res = tail

        return res

    new_properties = dict(ast.map(lambda k, v: flatten(v, base)))
    return ast.__class__(**new_properties)
