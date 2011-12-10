from lxml import etree

from codega import logger
from codega.error import ParseError
from codega.visitor import ClassVisitor, visitor
from codega.source import XmlSource, validate_xml
from codega.version import Version
from codega.rsclocator import ModuleLocator

import structures
from update import UpdateVisitor
from saver import save_config

class ParseVisitor(ClassVisitor):
    '''Parse the configs XML tree representation to the internal representation.'''

    def __init__(self):
        super(ParseVisitor, self).__init__()

        self._current_node = None

    def visit(self, node, xml_node):
        self._current_node = xml_node
        try:
            super(ParseVisitor, self).visit(node, xml_node)

        except Exception, e:
            if isinstance(e, ParseError):
                raise

            logger.error("Exception caught: %s" % e)
            raise ParseError("XML entry invalid (see line %s)" % self._current_node.sourceline)

    @visitor(structures.ModuleReference)
    def module_reference(self, node, xml_node):
        node.load_from_string(xml_node.text)

    @visitor(structures.Source)
    def source(self, node, xml_node):
        node.name = xml_node.find('name').text

        resource = xml_node.find('resource').text
        node.resource = '' if not resource else resource

        parser = xml_node.find('parser')
        if parser is not None:
            self.visit(node.parser, parser)

    @visitor(structures.Settings.RecursiveContainer)
    def recursive_container(self, node, xml_node):
        for chld in xml_node:
            if chld.tag == 'entry':
                node[chld.attrib['name']] = chld.text

            else:
                new_node = node[chld.attrib['name']] = structures.Settings.RecursiveContainer()
                self.visit(new_node, chld)

    @visitor(structures.Settings)
    def settings(self, node, xml_node):
        self.visit(node.data, xml_node)

    @visitor(structures.Target)
    def target(self, node, xml_node):
        node.source = xml_node.find('source').text
        node.filename = xml_node.find('target').text
        self.visit(node.generator, xml_node.find('generator'))

        settings_xml = xml_node.find('settings')
        if settings_xml is not None:
            self.visit(node.settings, settings_xml)

    @visitor(structures.PathList)
    def path_list(self, node, xml_node):
        for chld in xml_node:
            if chld.tag == 'target':
                node.destination = chld.text

            else:
                node.paths.append(chld.text)

    @visitor(structures.Copy)
    def copy(self, node, xml_node):
        node.source = xml_node.find('source').text
        node.target = xml_node.find('target').text

    @visitor(structures.Config)
    def config(self, node, xml_node):
        node.version = xml_node.attrib['version']
        for chld in xml_node:
            if chld.tag == 'paths':
                self.visit(node.paths, chld)

            elif chld.tag == 'external':
                node.external.append(chld.text.strip())

            elif chld.tag == 'source':
                source = structures.Source(node)
                self.visit(source, chld)
                node.sources[source.name] = source

            elif chld.tag == 'target':
                target = structures.Target(node)
                self.visit(target, chld)
                node.targets[target.filename] = target

            elif chld.tag == 'copy':
                copy = structures.Copy(node)
                self.visit(copy, chld)
                node.copy[copy.target] = copy

class ConfigXmlSource(XmlSource):
    '''XML source. This is the default source'''

    def load_fileobj(self, fileobj):
        # Parse raw XML file
        try:
            xml_root = super(ConfigXmlSource, self).load_fileobj(fileobj)

        except Exception, e:
            raise ParseError("Could not load source XML: %s" % e, 0)

        return self.parse_config_xml(xml_root.getroot())

    def parse_config_xml(self, xml_root):
        # Update the XML tree if needed (this needs pre-verifying the version)
        if not xml_root.attrib.has_key('version'):
            raise ParseError("Configuration version cannot be determined", 1)

        try:
            version = Version.load_from_string(xml_root.attrib['version'])

        except ValueError:
            raise ParseError("Invalid version format %s" % xml_root.attrib['version'], 1)

        xml_root = UpdateVisitor().visit(version, xml_root)

        # Validate the XML root with the config.xsd. The config.xsd file always
        # refers to the current version (see UpdateVisitor.version_current)
        try:
            validate_xml(xml_root, resource = 'config.xsd', resource_locator = ModuleLocator(__import__(__name__)))

        except etree.DocumentInvalid, e:
            raise ParseError('Configuration is invalid', e.error_log.last_error.line)

        # Initialize configuration object
        config = structures.Config()

        # Parse the XML structure
        visitor = ParseVisitor()
        try:
            visitor.visit(config, xml_root)

        except Exception, e:
            raise ParseError(str(e), visitor._current_node.sourceline)

        return config
