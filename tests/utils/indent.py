from unittest import TestCase

from codega.utils.indent import *

class TestIndent(TestCase):
    def test_indent(self):
        '''Indentation helper function works properly.'''

        self.assertEqual(indent('One liner'), '  One liner')
        self.assertEqual(indent(''), '')
        self.assertEqual(indent('   '), '')
        self.assertEqual(indent('   ', strip_result=False), '')
        self.assertEqual(indent('', strip_result=False, indent_empty_lines=True), '  ')
        self.assertEqual(indent('x ', strip_result=False), '  x ')
        self.assertEqual(indent('x\n\nx', indent_empty_lines=True), '  x\n\n  x')
        self.assertEqual(indent('', indent_empty_lines=True), '')

        self.assertEqual(indent('x', indent_string='*'), '*x')
        self.assertEqual(indent('x', level=3, indent_string='*'), '***x')

    def test_deindent(self):
        '''Deindentation works properly.'''

        self.assertEqual(deindent(''), '')
        self.assertEqual(deindent(' abc'), 'abc')
        self.assertEqual(deindent('   \n   \n \n    \n', lstrip=False, rstrip=False), '\n\n\n\n')
        self.assertEqual(deindent('  a\n   b'), 'a\n b')

        self.assertRaises(ValueError, deindent, '  a\n b')
        self.assertEqual(deindent('  a\n b', ignore_wrong_indentation=True), 'a\nb')

        self.assertEqual(deindent('   a\n   b', level=2), ' a\n b')

        self.assertEqual(deindent('   a\n   b\n\n\n\n\n', rstrip=True), 'a\nb')

    def test_c_multi_comment(self):
        '''C multi-line commenting works.'''

        self.assertEqual(c_multi_comment(''), '/*\n *\n */')
        self.assertEqual(c_multi_comment('text'), '/*\n * text\n */')
        self.assertEqual(c_multi_comment('text\n\n'), '/*\n * text\n *\n *\n */')

    def test_hash_comment(self):
        '''Hash commenting works.'''

        self.assertEqual(hash_comment(''), '#')
        self.assertEqual(hash_comment('text'), '# text')
        self.assertEqual(hash_comment('text\n\n'), '# text\n#\n#')

    def test_disclaimer(self):
        '''Disclaimer generation works properly.'''

        context = type('context', (object,), dict(source='a', target='b', parser='c', generator='d'))
        discl = disclaimer(context)
        self.assertEqual(discl, '# THIS IS AN AUTOMATICALLY GENERATED FILE. ALL MANUAL MODIFICATIONS TO IT MAY\n# BE LOST AT ANY TIME! MODIFY THE TEMPLATE INSTEAD (see below)\n#\n# Source file         a\n# Parser class        c\n# Target file         b\n# Generator class     d')

        discl = disclaimer(context, comment=lambda s: s)
        self.assertEqual(discl, 'THIS IS AN AUTOMATICALLY GENERATED FILE. ALL MANUAL MODIFICATIONS TO IT MAY\nBE LOST AT ANY TIME! MODIFY THE TEMPLATE INSTEAD (see below)\n\nSource file         a\nParser class        c\nTarget file         b\nGenerator class     d')
