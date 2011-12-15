'''
Alternate config file format. This is a specific language for an
alternative, non-XML config format. The config gets turn into an
XML so all validation logic stays the same.
'''

from ply import lex, yacc
from lxml import etree

from codega.error import ParseError
from codega import logger
from codega.config import latest_version

from xml import ConfigXmlSource

class Lexer(object):
    keywords = (
        'of', 'is', 'load', 'with', 'generate',
        'file', 'path', 'target', 'source',
        'from', 'copy', 'add', 'set',
        'to', 'external',
    )

    tokens = tuple(map(str.upper, keywords)) + (
        'STRING', 'NL',
    )

    t_ignore = ' \t'

    def __init__(self):
        self.lexer = lex.lex(module = self)
        self.lineno = 1
        self.linestart = 0
        self.filename = 'unknown'

        self.errors = 0

    def token(self):
        res = self.lexer.token()
        if res is not None:
            res.column = res.pos
            res.lineno = self.lexer.lexpos - self.linestart

        return res

    def t_keyword(self, t):
        r'[^\'\s][^\s]*'

        if t.value in self.keywords:
            t.type = t.value.upper()

        else:
            t.type = 'STRING'

        return t

    def t_STRING(self, t):
        r'\'[^\']+\''

        t.value = t.value[1:-1].replace('\\\'', '\'')
        return t

    def t_NL(self, t):
        r'(\r?\n)+'

        self.lineno += t.value.count('\n')
        self.linestart = t.lexpos + len(t.value)
        return t

    def t_error(self, t):
        logger.error('Cannot parse character, skipping; character=%r, line=%d, column=%d' % (t.value[0], self.lineno, self.lexer.lexpos - self.linestart))
        self.lexer.skip(1)
        self.errors += 1

class Parser(object):
    def __init__(self):
        self.lexer_obj = Lexer()
        self.lexer = self.lexer_obj.lexer
        self.tokens = self.lexer_obj.tokens
        self.parser = yacc.yacc(module = self)

        self.sections = None
        self.target_path = None

    def token(self):
        return self.lexer_obj.token()

    def parse(self, data):
        self.sections = dict(paths = [], externals = [], sources = [], targets = [], copies = [])
        try:
            return self.parser.parse(data)

        finally:
            self.sections = None
            self.target_path = None

    # RULES
    start = 'root'
    def p_root(self, p):
        '''root : productions'''

        p[0] = etree.Element('config', attrib = dict(version = str(latest_version)))

        if self.target_path is None:
            raise ParseError("Target path not specified")

        paths = etree.Element('paths')
        paths.append(self.target_path)
        paths.extend(self.sections['paths'])
        p[0].append(paths)
        p[0].extend(self.sections['externals'])
        p[0].extend(self.sections['sources'])
        p[0].extend(self.sections['targets'])
        p[0].extend(self.sections['copies'])

    def p_productions_0(self, p):
        '''productions : '''

    def p_productions_1(self, p):
        '''productions : path productions
                       | source productions
                       | target productions
                       | copy_rule productions
                       | external productions'''

    def p_path_0(self, p):
        '''path : PATH OF TARGET IS STRING NL'''

        if self.target_path is not None:
            raise ParseError("Target path already specified")

        self.target_path = etree.Element('target')
        self.target_path.text = p[5]

    def p_path_1(self, p):
        '''path : ADD PATH STRING NL'''

        path = etree.Element('path')
        path.text = p[3]
        self.sections['paths'].append(path)

    def p_source(self, p):
        '''source : LOAD SOURCE STRING FROM STRING NL
                  | LOAD SOURCE STRING FROM STRING WITH STRING NL'''

        source = etree.Element('source')

        name = etree.Element('name')
        name.text = p[3]
        source.append(name)

        resource = etree.Element('resource')
        resource.text = p[5]
        source.append(resource)

        if len(p) > 7:
            parser = etree.Element('parser')
            parser.text = p[7]
            source.append(parser)

        self.sections['sources'].append(source)

    def p_target(self, p):
        '''target : GENERATE TARGET FILE STRING WITH STRING FROM STRING NL settings'''

        target = etree.Element('target')

        source = etree.Element('source')
        source.text = p[8]
        target.append(source)

        generator = etree.Element('generator')
        generator.text = p[6]
        target.append(generator)

        targetf = etree.Element('target')
        targetf.text = p[4]
        target.append(targetf)

        target.append(self.collect_settings(p[10]))
        self.sections['targets'].append(target)

    def collect_settings(self, settings):
        def __collector(settingdict, target_tag = 'container'):
            res = etree.Element(target_tag)
            for key, value in settingdict.items():
                if isinstance(value, dict):
                    cont = __collector(value)
                    cont.attrib['name'] = key
                    res.append(cont)

                else:
                    entry = etree.Element('entry', name = key)
                    entry.text = value
                    res.append(entry)

            return res

        return __collector(settings, 'settings')

    def p_settings_0(self, p):
        '''settings : '''

        p[0] = {}

    def p_settings_1(self, p):
        '''settings : SET STRING TO STRING NL settings'''

        def __split(key, value, dest):
            if '.' not in key:
                if key in dest:
                    raise ParseError("Key %s set multiple times" % p[2])

                dest[key] = value

            else:
                head, tail = key.split('.', 1)
                if head in dest:
                    if not isinstance(dest[head], dict):
                        raise ParseError("Key %s set multiple times" % p[2])

                else:
                    dest[head] = {}

                __split(tail, value, dest[head])

        p[0] = p[6]
        __split(p[2], p[4], p[0])

    def p_copy(self, p):
        '''copy_rule : COPY STRING TO STRING NL'''

        copy = etree.Element('copy')

        source = etree.Element('source')
        source.text = p[2]
        copy.append(source)

        target = etree.Element('target')
        target.text = p[4]
        copy.append(target)

        self.sections['copies'].append(copy)

    def p_external(self, p):
        '''external : EXTERNAL STRING NL'''

        external = etree.Element('external')
        external.text = p[2]
        self.sections['externals'].append(external)

    def p_error(self, t):
        logger.error('Invalid token found; token=%r' % t)

class ConfigCustomSource(ConfigXmlSource):
    def load_fileobj(self, fileobj):
        xml_root = Parser().parse(fileobj.read())
        return self.parse_config_xml(xml_root)
