include ../makefile.include

all: entries.py

clean:
	rm -f output.txt

entries.py: entries.csv
	$(CGX) -o $@ -s $< -g csvgenerator:PyGen -p csvparser:CSVParser -l $(LOGLEVEL)
