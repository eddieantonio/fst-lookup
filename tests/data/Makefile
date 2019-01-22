eat.att.gz: eat.lexc

%.att.gz: %.lexc
	printf 'read lexc %s\nsave stack %s' $< $@ | foma -p

%: %.gz
	gunzip --force --keep $<
