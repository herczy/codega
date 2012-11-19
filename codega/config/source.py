from lxml import etree

from codega.visitor import XmlVisitor, visitor
from codega.source import XmlSource, validate_xml
from codega.version import Version
from codega.rsclocator import ModuleLocator

import structures
from update import UpdateVisitor

class ParseError(Exception):
    '''The given source could not be parsed'''

    def __init__(self, msg, lineno):
        super(ParseError, self).__init__("%s (at line %d)" % (msg, lineno))

class ParseVisitor(XmlVisitor):
    def __init__(self):
        super(ParseVisitor, self).__init__()

        self.current_node = None

    def visit(self, node, *args, **kwargs):
        self.current_node = node
        return super(ParseVisitor, self).visit(node, *args, **kwargs)

    def get_text(self, node, key, default=None):
        item = node.find(key)
        if item is None:
            return default

        return item.text.strip()

    def process_settings(self, node):
        if node is not None:
            return self.visit(node)
        return ()

    @visitor('config')
    def visit_config(self, node):
        self._builder = structures.StructureBuilder()
        for child in node:
            self.visit(child)

        return self._builder.config

    @visitor('paths')
    def visit_paths(self, node):
        for child in node:
            value = child.text.strip()
            if child.tag == 'target':
                self._builder.set_destination(value)

            else:
                self._builder.add_include(value)

    @visitor('source')
    def visit_source(self, node):
        name = self.get_text(node, 'name')
        resource = self.get_text(node, 'resource')
        parser = self.get_text(node, 'parser')
        transform = (child.text.strip() for child in node if child.tag == 'transform')

        self._builder.add_source(name, resource, parser=parser, transform=transform)

    @visitor('target')
    def visit_target(self, node):
        source = self.get_text(node, 'source')
        generator = self.get_text(node, 'generator')
        filename = self.get_text(node, 'target')
        settings = self.process_settings(node.find('settings'))

        self._builder.add_target(source, filename, generator, settings=settings)

    @visitor('copy')
    def visit_copy(self, node):
        source = self.get_text(node, 'source')
        target = self.get_text(node, 'target')

        self._builder.add_copy(source, target)

    @visitor('module')
    def visit_module(self, node):
        name = node.attrib['name']
        reference = self.get_text(node, 'reference')
        settings = self.process_settings(node.find('settings'))

        self._builder.add_module(name, reference, settings=settings)

    @visitor('external')
    def visit_external(self, node):
        self._builder.add_external(node.text.strip())

    @visitor('settings')
    def visit_settings(self, node):
        res = []
        for child in node:
            res.extend(self.visit(child, ()))

        return res

    @visitor('container')
    def visit_container(self, node, keystub):
        res = []
        for child in node:
            res.extend(self.visit(child, keystub + (node.attrib['name'],)))

        return res

    @visitor('entry')
    def visit_entry(self, node, keystub):
        return [(keystub + (node.attrib['name'],), node.text.strip())]

class ConfigSource(XmlSource):
    '''XML source. This is the default source'''

    def load_fileobj(self, fileobj):
        # Parse raw XML file
        try:
            xml_root = super(ConfigSource, self).load_fileobj(fileobj)

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
            validate_xml(xml_root, resource='config.xsd', resource_locator=ModuleLocator(__import__(__name__)))

        except etree.DocumentInvalid, e:
            raise ParseError('Configuration is invalid', e.error_log.last_error.line)

        # Parse the XML structure
        visitor = ParseVisitor()
        try:
            return visitor.visit(xml_root)

        except Exception, e:
            raise ParseError(str(e), visitor.current_node.sourceline)
