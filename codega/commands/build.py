import sys
import optparse

from codega.rsclocator import FileResourceLocator
from codega.config import Config
from codega.generator import GeneratorBase
from codega.context import Context
from codega.error import ResourceError
from codega import logger

from base import OptparsedCommand
from make import build_target

def build_config(source, parser, target, generator):
    from lxml import etree

    def make_text_node(tag, text):
        element = etree.Element(tag)
        element.text = text
        return element

    xml_paths = etree.Element('paths')
    xml_paths.append(make_text_node('target', '.'))
    xml_paths.append(make_text_node('path', '.'))

    xml_source = etree.Element('source')
    xml_source.append(make_text_node('name', 'source'))
    xml_source.append(make_text_node('filename', source))
    if parser is not None:
        xml_source.append(make_text_node('parser', parser))

    xml_target = etree.Element('target')
    xml_target.append(make_text_node('source', 'source'))
    xml_target.append(make_text_node('generator', generator))
    xml_target.append(make_text_node('target', target))

    xml = etree.Element('config')
    xml.attrib['version'] = '1.0'
    xml.append(xml_paths)
    xml.append(xml_source)
    xml.append(xml_target)

    rsc = FileResourceLocator([ '.' ])
    return Config(xml, system_locator = rsc)

class CommandBuild(OptparsedCommand):
    def __init__(self):
        options = [
            optparse.make_option('-s', '--source', default = None,
                                 help = 'Specify the source file'),
            optparse.make_option('-p', '--parser', default = 'codega.source:XmlSource',
                                 help = 'Specify the parser in <module>:<source class> format (default: %default)'),
            optparse.make_option('-t', '--target', default = 'sys.stdout',
                                 help = 'Specify the target file (default: sys.stdout)'),
            optparse.make_option('-g', '--generator', default = None,
                                 help = 'Specify the generator in <module>:<source class> format'),
            optparse.make_option('-d', '--debug', default = False, action = 'store_true',
                                 help = 'Produce debug output'),
        ]

        super(CommandBuild, self).__init__('build', options, helpstring = 'Build the source with specified generator')

    def execute(self):
        if not self.opts.source:
            print >>sys.stderr, 'Missing source'
            return False

        if not self.opts.generator:
            print >>sys.stderr, 'Missing generator'
            return False

        config = build_config(self.opts.source, self.opts.parser, self.opts.target, self.opts.generator)

        target = config.targets[0]
        build_target(config, target)
        return True
