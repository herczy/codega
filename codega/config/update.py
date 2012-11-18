from codega.config import latest_version

from codega.visitor import ExplicitVisitor, visitor
from codega.version import Version

class VersionMismatchError(Exception):
    '''The version isn't what it supposed to be'''

class UpdateVisitor(ExplicitVisitor):
    '''To be able to handle different versions, we need to 'update' the
    current version. So if a new compatible config version appears we need
    to add an update function to that version.

    Since there is only one supported version, only the fallback and the current
    version visitors will be defined.

    The update must be done prior to validating the XML. So the XSD always validates
    the current version.

    Version history:
    * 1.0 -- Initial version
    * 1.1 -- Renamed /config/source/filename to /config/source/resource since in this
             version we accept non-file based sources too.
    * 1.2 -- Added 'external' tag so other config files could be built from the config.
             This also means that the mandatory minimum count of targets/sources and paths
             changes to 0 since the externals define other kinds of tasks and paths for
             themselves and the config can be used to tie other configs together.
    * 1.3 -- Added 'copy' tag so a file can be copied to it's destination.
    * 1.4 -- Added 'transform' tag to sources. Transformations are module refs that can
             be used to transform the source to a different structure.
    * 1.5 -- Module reference format changed. Now instead of ':' the module and class
             separator is '.'
    '''

    @visitor(Version(1, 0))
    def update_1_0(self, version, xml_root):
        '''Update 1.0 configs to 1.1'''

        for node in xml_root.findall('source/filename'):
            node.tag = 'resource'
        xml_root.attrib['version'] = '1.1'
        return self.visit(Version(1, 1), xml_root)

    @visitor(Version(1, 1), Version(1, 2), Version(1, 3), Version(1, 4), latest_version)
    def version_current(self, version, xml_root):
        '''Formats that don't need further change'''

        return xml_root

    def visit_fallback(self, version, xml_root):
        raise VersionMismatchError("Configs with version %s are not supported" % version)

