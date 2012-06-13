include ../makefile.include

all: output.txt

clean:
	rm -f output.txt

output.txt: input.xml
	$(CGX) -o $@ -s $< -g ../basic/dumper:DumpGenerator -p parsedump:TestParser -l $(LOGLEVEL)
