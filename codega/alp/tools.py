'''
AULAPA tools. These are functions that are too
small be put into separate modules.
'''

import re
import os

import atexit


replacement_regex = re.compile(r'\@([a-zA-Z_][a-zA-Z0-9_]+)\@')


def replace(text, **bindings):
    '''
    Replace @[a-zA-Z_][a-zA-Z0-9_]+@ tokens from bindings
    '''

    def __replacement_function(match):
        return bindings[match.group(1)]

    global replacement_regex
    return replacement_regex.sub(__replacement_function, text).replace('@@', '@')


cleanup_file_list = []


def __cleanup_files():
    '''
    At exit, clean up file names in cleanup_file_list.
    '''

    global cleanup_file_list

    for filename in cleanup_file_list:
        if os.path.isfile(filename):
            os.remove(filename)


atexit.register(__cleanup_files)
