include ../makefile.include

all: output.txt

clean:
	rm -f output.txt

output.txt: input.xml
	$(CGX) -o $@ -s $< -g dumper:DumpGenerator -l $(LOGLEVEL)
