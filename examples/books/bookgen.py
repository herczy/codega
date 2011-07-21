from codega.template import *
from codega.generator import *

from codega.cgextra.makowrapper import inline
from codega.cgextra import matcher

class BookGenerator(ObjectGenerator):
    @inline(matcher = matcher.tag('bookshelf'))
    def generator_main(self, source, context):
        '''
        #include <stdio.h>
        #include <stdlib.h>
        #include <stdint.h>
        #include <string.h>

        typedef struct _Books
        {
          const char *title;
          const char *author;
          const char *published;
        } Books;

        const Books booklist[];

        int main()
        {
          int i;

          for (i = 0; booklist[i].title; ++i)
            printf("%s (%s) by %s\\n", booklist[i].title, booklist[i].published, booklist[i].author);

          return 0;
        }

        const Books booklist[] = {
        % for book in books:
          ${book}
        % endfor
          { NULL, NULL, NULL },
        };
        '''

        return dict(books = context.map(self, source))

    @inline(matcher = matcher.tag('book'))
    def generator_book(self, source, context):
        '''{ "${str(title)}", "${str(author)}", "${str(published)}" },'''

        bindings = Bindings()

        bindings.title = source.find('title').text
        bindings.author = source.find('author').text
        bindings.published = source.find('pubdate').text

        return bindings
