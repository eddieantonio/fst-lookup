LEXC = $(wildcard *.lexc)
all: $(LEXC:.lexc=.fomabin) tae.fomabin

### Concrete targets ###
# Flips the eat FST, because sometimes your FSTs are upside-down 🙃
tae.fomabin: eat.fomabin
	printf 'load stack %s\ninvert net\nsave stack %s' $< $@ | foma -p

### Pattern rules ###

# Compile a LEXC file to an FST.
%.fomabin: %.lexc
	printf 'read lexc %s\nsave stack %s' $< $@ | foma -p

# Compile an XFST script to an FST.
%.fomabin: %.xfst
	foma -l $< -e 'save stack $@' -s

# See the FST as a plain-text file.
%.txt: %.fomabin
	cat $< | gunzip > $@

# See the FST as a graph.
%.dot: %.fomabin
	foma -q -e 'load $<' -e 'print dot > $@' -s

# Convert graphs to PDFs.
%.pdf: %.dot
	dot -Tpdf -o$@ $<

.PHONY: all
