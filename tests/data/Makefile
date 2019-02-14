LEXC = $(wildcard *.lexc)
all: $(LEXC:.lexc=.fomabin)

%.fomabin: %.lexc
	printf 'read lexc %s\nsave stack %s' $< $@ | foma -p

%.txt: %.fomabin
	cat $< | gunzip > $@


%.dot: %.fomabin
	foma -q -e 'load $<' -e 'print dot > $@' -s

%.pdf: %.dot
	dot -Tpdf -o$@ $< 

.PHONY: all
