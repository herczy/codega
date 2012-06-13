include ../makefile.include

all: books.c books.html

clean:
	rm -f books.c books.html

books.c: books.xml
	$(CGX) -s $< -o $@ -g bookgen:CBookGenerator -l $(LOGLEVEL)

books.html: books.xml
	$(CGX) -s $< -o $@ -g bookgen:HtmlBookGenerator -l $(LOGLEVEL)
