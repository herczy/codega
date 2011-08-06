import sys

from lxml import etree

from codega.source import SourceBase
from codega import logger

class BookSource(SourceBase):
    def load(self, resource):
        bookshelf = etree.Element('bookshelf')
        for line in sys.stdin.read().split('\n'):
            line = line.strip()
            if line == '':
                break

            if line.count(',') != 2:
                logger.warning('Invalid book entry %s, ignoring it', line)
                continue

            title, author, pubdate = map(str.strip, line.split(','))
            print title, author, pubdate

            book = etree.Element('book')

            cur = etree.Element('title')
            cur.text = title
            book.append(cur)

            cur = etree.Element('author')
            cur.text = author
            book.append(cur)

            cur = etree.Element('pubdate')
            cur.text = pubdate
            book.append(cur)

            bookshelf.append(book)

        return etree.ElementTree(element = bookshelf)
