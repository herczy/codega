'''Wrapper module for importing the proper StringIO class'''

try:
    from cStringIO import StringIO

except ImportError, e:
    if str(e) != 'No module named cStringIO':
        raise

    from StringIO import StringIO
