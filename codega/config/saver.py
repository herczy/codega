from lxml import etree

from codega.visitor import ClassVisitor, visitor

import structures

class SaveError(Exception):
    '''Errors with saving a configuration structure'''

def build_element(tag, attributes={}, text=None, children=[]):
    res = etree.Element(tag)
    if text is not None:
        res.text = text
    for k, v in attributes.iteritems():
        res.attrib[k] = v
    res.extend(children)
    return res

class SaveVisitor(ClassVisitor):
    '''Parse the internal config representation into an XML tree representation'''

    @visitor(structures.ModuleReference)
    def module_reference(self, node):
        return '%s:%s' % (node.module, node.reference)

    @visitor(structures.Source)
    def source(self, node):
        res = build_element('source', children=[
                  build_element('name', text=node.name),
                  build_element('resource', text=node.resource),
              ])

        if not node.parser.is_default:
            res.append(build_element('parser', text=self.visit(node.parser)))

        for transform in node.transform:
            res.append(build_element('transform', text=self.visit(transform)))

        return res

    @visitor(structures.Settings.RecursiveContainer)
    def recursive_container(self, node):
        res = []
        for name, value in node.iteritems():
            if isinstance(value, basestring):
                res.append(build_element('entry', attributes={ 'name' : name }, text=value))

            else:
                res.append(build_element('container', attributes={ 'name' : name }, children=self.visit(value)))

        return res

    @visitor(structures.Settings)
    def settings(self, node):
        return build_element('settings', children=self.visit(node.data))

    @visitor(structures.Target)
    def target(self, node):
        res = etree.Element('target')
        res.append(build_element('source', text=node.source))
        res.append(build_element('generator', text=self.visit(node.generator)))
        res.append(build_element('target', text=node.filename))

        if not node.settings.empty:
            res.append(self.visit(node.settings))

        return res

    @visitor(structures.PathList)
    def path_list(self, node):
        res = build_element('paths')
        res.append(build_element('target', text=node.destination))
        for path in node.paths:
            res.append(build_element('path', text=path))

        return res

    @visitor(structures.Copy)
    def copy(self, node):
        return build_element('copy', children=[build_element('source', text=node.source), build_element('target', text=node.target)])

    @visitor(structures.Config)
    def config(self, node):
        res = etree.Element('config')
        res.attrib['version'] = str(node.version)
        res.append(self.visit(node.paths))
        res.extend([build_element('external', text=ext) for ext in node.external])
        res.extend([self.visit(source) for source in node.sources.values()])
        res.extend([self.visit(target) for target in node.targets.values()])
        res.extend([self.visit(copy) for copy in node.copy.values()])

        return res

def save_config(config):
    try:
        return etree.tostring(SaveVisitor().visit(config), pretty_print=True)

    except Exception, e:
        raise SaveError('Error detected while saving the config: %s' % e)
