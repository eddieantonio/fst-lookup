all:
	@echo "Please invoke one of the following instead: "
	@awk '/^#: / {sub(/#: /, "\t"); print $$0}' $(firstword $(MAKEFILE_LIST))
	@false

#: release - push a new release to GitHub
release: sync-version
	version="v$(shell poetry run python3 libexec/print-version.py)" && \
		git commit -a -m "$$version" &&\
		git tag "$$version"
	git push
	git push --tags

#: sync-version - keep package version in sync with pyproject.toml
sync-version: fst_lookup/__version__.py

#: clean - remove build artifacts
clean:
	$(RM) -r setup.py build dist $(wildcard *.egg-info) $(wildcard fst-lookup-*/)


############################## SPECIFIC TARGETS ##############################

fst_lookup/__version__.py: pyproject.toml
	poetry run python3 libexec/update-version.py

# This AWFUL command uses compiledb (https://github.com/nickdiego/compiledb)
# to automatically generate compile_commands.json
compile_commands.json: setup.py
	python3 setup.py build_ext --force | grep -E '^(clang|gcc)' | compiledb

.PHONY: all release sync-version new-version
