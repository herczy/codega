'''Indentation helper functions

Dependencies: None
'''

def indent(text, level = 1, indent_empty_lines = False, indent_string = ' '):
    '''General purpose indentation

    Arguments:
    text -- Text to indent. The text is split to lines and each line
            is individualy indented.
    indent_empty_lines -- If set, empty lines will be indented too.
    indent_string -- Before each line this string is copied level times.
    '''

    def __indent_line(line):
        if not indent_empty_lines and not line.strip():
            return ''

        return '%s%s' % (indent_string * level, line)

    return '\n'.join(map(__indent_line, text.split('\n')))

def c_multi_comment(text):
    '''C multi-line comment.

    The comment will look like this:
    /*
     * COMMENT TEXT
     */

    Arguments:
    text -- Text to indent
    '''

    def __line_comment(line):
        if not line.strip():
            return ' *'

        return ' * %s' % line

    return '\n'.join(map(__indent_line, text.split('\n')))
