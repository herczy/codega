import os.path
import sys

from lxml import etree
from codega.context import Context

def load_class(identifier, *args, **kwargs):
    if ':' not in identifier:
        raise ImportError("Invalid identifier %s" % identifier)

    mod_ident, cls_ident = identifier.rsplit(':', 1)

    # If identifier is a path, then split it
    if '/' in mod_ident:
        path, name = os.path.split(mod_ident)

    else:
        path, name = None, mod_ident

    added_path = False
    if path and path not in sys.path:
        sys.path.insert(0, path)
        added_path = True

    sys.path.insert(1, '.')
    try:
        mod = __import__(name, fromlist=[cls_ident])

    finally:
        del sys.path[0]
        if added_path:
            del sys.path[0]

    if not hasattr(mod, cls_ident):
        raise ImportError("Module has no attribute %s" % cls_ident)

    cls = getattr(mod, cls_ident)
    try:
        return cls(*args, **kwargs)

    except Exception, e:
        raise ImportError("Error initializing class: %s", e)

def build(source, parser, target, generator, settings):
    try:
        generator_obj = load_class(generator)

    except ImportError, e:
        print >> sys.stderr, "Cannot import generator module %s: %s" % (generator, e)
        return False

    try:
        parser_obj = load_class(parser)

    except ImportError, e:
        print >> sys.stderr, "Cannot import parser module %s: %s" % (parser, e)
        return False

    try:
        # Load and parse the task
        source = parser_obj.load(source)

    except:
        print >> sys.stderr, "Source could not be parsed"
        return False

    # Ugly kludge from the olden days, remove ASAP
    if isinstance(source, etree._ElementTree):
        source = source.getroot()

    context = Context(source, target, generator, parser, settings)
    try:
        result = generator_obj.generate(source, context)

    except:
        print >> sys.stderr, "Generation failed"
        return False

    with open(target, 'w') as out:
        out.write(result)

    return True
