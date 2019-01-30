all: eat.fomabin english-flags.fomabin

%.fomabin: %.lexc
	printf 'read lexc %s\nsave stack %s' $< $@ | foma -p

%.txt: %.fomabin
	cat $< | gunzip > $@

%.fomabin: %.fomatxt
	cat $< | gzip > $@
