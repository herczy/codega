'''Indentation helper functions

Dependencies: None
'''

def indent(text, level = 1, indent_empty_lines = False, indent_string = '  ', strip_result = True):
    '''General purpose indentation

    Arguments:
    text -- Text to indent. The text is split to lines and each line
            is individualy indented.
    indent_empty_lines -- If set, empty lines will be indented too.
    indent_string -- Before each line this string is copied level times.
    strip_result -- If set, each line is right-stripped in the result
    '''

    def __indent_line(line):
        if not indent_empty_lines and not line.strip():
            return ''

        res = '%s%s' % (indent_string * level, line)
        if strip_result:
            res = res.rstrip()

        return res

    return '\n'.join(map(__indent_line, text.split('\n')))

def deindent(text, level = None, ignore_wrong_indentation = False, lstrip = True, rstrip = False):
    '''De-indent a text.
    
    Arguments:
    text -- Text to deindent
    level -- How many levels to deindent. If set to none and the text has a
             consistent indent, the indentation level is deduced automatically
    ignore_wrong_indentation -- If not set, wrongly indented lines will cause
                                an exception to occur (ValueError). If set, these
                                lines are left-stripped
    lstrip -- If set, empty lines are removed from the beginning
    rstrip -- If set, empty lines are removed from the end
    '''

    res = []
    indent_level = level if level is not None else None
    for line in text.split('\n'):
        if not line.strip():
            res.append('')
            continue

        if indent_level is None:
            for pos in xrange(len(line)):
                if not line[pos].isspace():
                    break

            else:
                # This can never happen! Or should not
                assert 0

            indent_level = pos

        if line[:indent_level].strip():
            # Wrong indentation!
            if ignore_wrong_indentation:
                line = line.lstrip()

            else:
                raise ValueError("Invalid line indentation")

        else:
            line = line[indent_level:]

        res.append(line)

    if lstrip:
        while not res[0]:
            del res[0]

    if rstrip:
        while not res[-1]:
            del res[-1]

    return '\n'.join(res)

def c_multi_comment(text):
    '''C multi-line comment.

    The comment will look like this:
    /*
     * COMMENT TEXT
     */

    Arguments:
    text -- Text to indent
    '''

    box = indent(text, indent_empty_lines = True, indent_string = ' * ')
    return '/*\n%s\n */' % box

def hash_comment(text):
    '''Python/Shell/etc. style multiline comment

    The commented text will look something like this:
    #
    # COMMENT TEXT
    #
    '''

    return indent(text, indent_empty_lines = True, indent_string = '# ')

def disclaimer(context, comment = hash_comment):
    '''Create a commented disclaimer.

    The disclaimer will look something like this:
    #
    # THIS FILE IS AUTOMATICALLY GENERATED, ...
    #
    '''

    targetfile = context.target.filename
    srcfile = context.source.resource
    prsref = str(context.source.parser)
    genref = str(context.target.generator)

    text = '''THIS IS AN AUTOMATICALLY GENERATED FILE. ALL MANUAL MODIFICATIONS TO IT MAY
BE LOST AT ANY TIME! MODIFY THE TEMPLATE INSTEAD (see below)

Source file         %(srcfile)s
Parser class        %(prsref)s
Target file         %(targetfile)s
Generator class     %(genref)s''' % locals()

    return comment(text)